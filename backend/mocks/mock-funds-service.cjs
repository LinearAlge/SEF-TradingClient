const http = require('http')
const fs = require('fs')
const path = require('path')

const PORT = process.env.PORT || 3021
const DB_PATH = path.join(__dirname, 'data', 'mock-funds-db.json')
const MARKET_DB_PATH = path.join(__dirname, 'data', 'mock-market-db.json')

const DEFAULT_DB = {
  accounts: {},
  cashFlows: [],
  passwords: {},
}

const DEFAULT_MARKET = {
  asOf: '',
  stocks: [],
}

const sendJson = (res, statusCode, payload) => {
  const body = JSON.stringify(payload)
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
  })
  res.end(body)
}

const parseJsonBody = (req, res, callback) => {
  let rawBody = ''
  req.on('data', (chunk) => {
    rawBody += chunk
    if (rawBody.length > 1e6) {
      req.destroy()
    }
  })

  req.on('end', () => {
    let payload = {}
    try {
      payload = rawBody ? JSON.parse(rawBody) : {}
    } catch (error) {
      sendJson(res, 400, { ok: false, message: '无效的 JSON 数据' })
      return
    }

    callback(payload)
  })
}

const formatAsOf = () => {
  const now = new Date()
  const offsetMs = 8 * 60 * 60 * 1000
  const local = new Date(now.getTime() + offsetMs)
  return local.toISOString().replace('Z', '+08:00')
}

const loadDb = () => {
  if (!fs.existsSync(DB_PATH)) {
    return { ...DEFAULT_DB }
  }

  try {
    const raw = fs.readFileSync(DB_PATH, 'utf8')
    const parsed = JSON.parse(raw)
    return { ...DEFAULT_DB, ...parsed }
  } catch (error) {
    return { ...DEFAULT_DB }
  }
}

const saveDb = (db) => {
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2), 'utf8')
}

const loadMarketDb = () => {
  if (!fs.existsSync(MARKET_DB_PATH)) {
    return { ...DEFAULT_MARKET }
  }

  try {
    const raw = fs.readFileSync(MARKET_DB_PATH, 'utf8')
    const parsed = JSON.parse(raw)
    return { ...DEFAULT_MARKET, ...parsed }
  } catch (error) {
    return { ...DEFAULT_MARKET }
  }
}

const buildMarketIndex = (market = {}) => {
  const index = {}
  ;(market.stocks || []).forEach((stock) => {
    index[stock.symbol] = stock
  })
  return index
}

const calculateMarketValue = (positions = [], marketIndex = {}) => {
  return positions.reduce((sum, position) => {
    const totalShares = (position.lots || []).reduce((lotSum, lot) => lotSum + lot.shares, 0)
    const lastPrice = Number(marketIndex[position.symbol]?.lastPrice ?? position.lastPrice ?? 0)
    return sum + totalShares * lastPrice
  }, 0)
}

const createCashFlow = (payload) => ({
  id: `CASH-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
  time: new Date().toLocaleString('zh-CN', { hour12: false }),
  status: '已完成',
  ...payload,
})

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    })
    res.end()
    return
  }

  if (req.url === '/health' && req.method === 'GET') {
    sendJson(res, 200, { ok: true })
    return
  }

  if (req.url.startsWith('/funds') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = db.accounts?.[account]

    if (!record) {
      sendJson(res, 404, { ok: false, message: '账户不存在' })
      return
    }

    const balances = record.balances || {}
    const available = Number(balances.available ?? 0)
    const frozen = Number(balances.frozen ?? 0)
    const marketDb = loadMarketDb()
    const marketIndex = buildMarketIndex(marketDb)
    const marketValue = calculateMarketValue(record.positions || [], marketIndex)
    const totalEquity = available + frozen + marketValue
    const updatedAt = marketDb.asOf || record.asOf || formatAsOf()

    sendJson(res, 200, {
      ok: true,
      account,
      fundAccountId: record.fundAccountId,
      currency: record.currency,
      available,
      frozen,
      marketValue,
      totalEquity,
      updatedAt,
    })
    return
  }

  if (req.url.startsWith('/accounts') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = db.accounts?.[account]

    if (!record) {
      sendJson(res, 404, { ok: false, message: '账户不存在' })
      return
    }

    sendJson(res, 200, {
      ok: true,
      account,
      phone: record.phone || '',
      idNumber: record.idNumber || '',
    })
    return
  }

  if (req.url === '/funds/apply-fill' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const side = payload.side
      const symbol = payload.symbol || ''
      const price = Number(payload.price)
      const quantity = Number(payload.quantity)

      if (!side || !symbol || !price || !quantity) {
        sendJson(res, 400, { ok: false, message: '清算参数不完整' })
        return
      }

      const db = loadDb()
      const record = db.accounts?.[account]
      if (!record) {
        sendJson(res, 404, { ok: false, message: '账户不存在' })
        return
      }

      record.balances = record.balances || { available: 0, frozen: 0 }
      const amount = Number((price * quantity).toFixed(2))
      const normalizedSide = side === 'buy' ? '买入' : side === 'sell' ? '卖出' : side

      if (normalizedSide === '买入') {
        record.balances.available = Math.max(0, record.balances.available - amount)
        db.cashFlows.unshift(
          createCashFlow({
            account,
            type: '买入成交',
            amount: `-${amount.toFixed(2)}`,
            status: '已完成',
            symbol,
            qty: quantity,
          }),
        )
      } else if (normalizedSide === '卖出') {
        record.balances.available += amount
        db.cashFlows.unshift(
          createCashFlow({
            account,
            type: '卖出成交',
            amount: `+${amount.toFixed(2)}`,
            status: '已完成',
            symbol,
            qty: quantity,
          }),
        )
      } else {
        sendJson(res, 400, { ok: false, message: '不支持的成交方向' })
        return
      }

      record.asOf = formatAsOf()
      saveDb(db)
      sendJson(res, 200, { ok: true })
    })
    return
  }

  if (req.url === '/passwords/trade/verify' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const password = payload.password
      const db = loadDb()
      const record = db.accounts?.[account]
      if (!record) {
        sendJson(res, 404, { ok: false, message: '账户不存在' })
        return
      }

      const storedPassword = db.passwords?.[account]?.trade
      if (!storedPassword) {
        sendJson(res, 400, { ok: false, message: '交易密码未设置' })
        return
      }

      if (!password || storedPassword !== password) {
        sendJson(res, 401, { ok: false, message: '交易密码错误' })
        return
      }

      sendJson(res, 200, { ok: true })
    })
    return
  }

  if (req.url.startsWith('/cash-flows') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const flows = (db.cashFlows || []).filter((item) => item.account === account)
    sendJson(res, 200, { ok: true, cashFlows: flows })
    return
  }

  if (req.url === '/funds/deposit' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const amount = Number(payload.amount)
      if (!amount || amount <= 0) {
        sendJson(res, 400, { ok: false, message: '存款金额必须大于 0' })
        return
      }

      const db = loadDb()
      const record = db.accounts?.[account]
      if (!record) {
        sendJson(res, 404, { ok: false, message: '账户不存在' })
        return
      }

      record.balances.available += amount
      db.cashFlows.unshift(
        createCashFlow({
          account,
          type: '入金',
          amount: `+${amount.toFixed(2)}`,
        }),
      )

      saveDb(db)
      sendJson(res, 200, { ok: true })
    })
    return
  }

  if (req.url === '/funds/withdraw' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const amount = Number(payload.amount)
      const password = payload.password
      if (!amount || amount <= 0) {
        sendJson(res, 400, { ok: false, message: '取款金额必须大于 0' })
        return
      }

      const db = loadDb()
      const record = db.accounts?.[account]
      if (!record) {
        sendJson(res, 404, { ok: false, message: '账户不存在' })
        return
      }

      const storedPassword = db.passwords?.[account]?.withdraw
      if (storedPassword && password && storedPassword !== password) {
        sendJson(res, 400, { ok: false, message: '取款密码错误' })
        return
      }

      if (amount > record.balances.available) {
        sendJson(res, 400, { ok: false, message: '取款金额超过可用资金' })
        return
      }

      record.balances.available -= amount
      db.cashFlows.unshift(
        createCashFlow({
          account,
          type: '出金',
          amount: `-${amount.toFixed(2)}`,
        }),
      )

      saveDb(db)
      sendJson(res, 200, { ok: true })
    })
    return
  }

  if (req.url === '/passwords/trade' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const { currentPassword, nextPassword } = payload
      if (!currentPassword || !nextPassword) {
        sendJson(res, 400, { ok: false, message: '密码信息不完整' })
        return
      }

      const db = loadDb()
      const stored = db.passwords?.[account]?.trade
      if (stored && stored !== currentPassword) {
        sendJson(res, 400, { ok: false, message: '当前密码不正确' })
        return
      }

      db.passwords = db.passwords || {}
      db.passwords[account] = db.passwords[account] || {}
      db.passwords[account].trade = nextPassword
      saveDb(db)
      sendJson(res, 200, { ok: true })
    })
    return
  }

  if (req.url === '/passwords/withdraw' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const { currentPassword, nextPassword } = payload
      if (!currentPassword || !nextPassword) {
        sendJson(res, 400, { ok: false, message: '密码信息不完整' })
        return
      }

      const db = loadDb()
      const stored = db.passwords?.[account]?.withdraw
      if (stored && stored !== currentPassword) {
        sendJson(res, 400, { ok: false, message: '当前密码不正确' })
        return
      }

      db.passwords = db.passwords || {}
      db.passwords[account] = db.passwords[account] || {}
      db.passwords[account].withdraw = nextPassword
      saveDb(db)
      sendJson(res, 200, { ok: true })
    })
    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Mock funds service running at http://localhost:${PORT}`)
})
