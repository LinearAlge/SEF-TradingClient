const http = require('http')
const fs = require('fs')
const path = require('path')

const PORT = process.env.PORT || 3022
const DB_PATH = path.join(__dirname, 'data', 'mock-securities-db.json')
const MARKET_DB_PATH = path.join(__dirname, 'data', 'mock-market-db.json')

const DEFAULT_DB = {
  accounts: {},
  stockFlows: [],
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

const buildHoldingSummary = (positions = [], marketIndex = {}) => {
  return positions.map((position) => {
    const stock = marketIndex[position.symbol]
    const name = stock?.name || position.name || position.symbol
    const lastPrice = Number(stock?.lastPrice ?? position.lastPrice ?? 0)
    const lots = position.lots || []
    const totalShares = lots.reduce((sum, lot) => sum + lot.shares, 0)
    const totalCost = lots.reduce((sum, lot) => sum + lot.price * lot.shares, 0)
    const costPrice = totalShares ? totalCost / totalShares : 0
    const marketValue = totalShares * lastPrice
    const pnlAmount = marketValue - totalCost
    const pnlRate = totalCost ? pnlAmount / totalCost : 0
    const availableShares = position.availableShares ?? totalShares
    const frozenShares = position.frozenShares ?? Math.max(totalShares - availableShares, 0)

    return {
      symbol: position.symbol,
      name,
      shares: totalShares,
      availableShares,
      frozenShares,
      costPrice,
      lastPrice,
      pnlAmount,
      pnlRate,
    }
  })
}

const createStockFlow = (payload) => ({
  id: `STOCK-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
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

  if (req.url.startsWith('/holdings') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = db.accounts?.[account]

    if (!record) {
      sendJson(res, 404, { ok: false, message: '账户不存在' })
      return
    }

    const marketDb = loadMarketDb()
    const marketIndex = buildMarketIndex(marketDb)
    const holdings = buildHoldingSummary(record.positions || [], marketIndex)
    const totalMarketValue = holdings.reduce((sum, item) => sum + item.lastPrice * item.shares, 0)
    const asOf = marketDb.asOf || record.asOf || formatAsOf()

    sendJson(res, 200, {
      ok: true,
      account,
      securitiesAccountId: record.securitiesAccountId,
      asOf,
      totalMarketValue,
      holdings,
    })
    return
  }

  if (req.url === '/positions/apply-fill' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const side = payload.side
      const symbol = (payload.symbol || '').trim()
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

      record.positions = record.positions || []
      const normalizedSide = side === 'buy' ? '买入' : side === 'sell' ? '卖出' : side
      let position = record.positions.find((item) => item.symbol === symbol)
      if (!position) {
        position = { symbol, lots: [], availableShares: 0, frozenShares: 0 }
        record.positions.push(position)
      }

      position.lots = position.lots || []

      if (normalizedSide === '买入') {
        position.lots.push({ price, shares: quantity })
        position.availableShares = Number(position.availableShares ?? 0) + quantity
      } else if (normalizedSide === '卖出') {
        let remaining = quantity
        const currentAvailable = Number(
          position.availableShares ?? position.lots.reduce((sum, lot) => sum + lot.shares, 0),
        )
        position.availableShares = Math.max(0, currentAvailable - remaining)
        for (const lot of position.lots) {
          if (remaining <= 0) break
          const take = Math.min(lot.shares, remaining)
          lot.shares -= take
          remaining -= take
        }
        position.lots = position.lots.filter((lot) => lot.shares > 0)
        if (position.lots.length === 0) {
          position.availableShares = 0
          record.positions = record.positions.filter((item) => item.symbol !== symbol)
        }
      } else {
        sendJson(res, 400, { ok: false, message: '不支持的成交方向' })
        return
      }

      db.stockFlows = db.stockFlows || []
      db.stockFlows.unshift(
        createStockFlow({
          account,
          type: normalizedSide === '买入' ? '买入成交' : '卖出成交',
          symbol,
          qty: String(quantity),
        }),
      )
      record.asOf = formatAsOf()
      saveDb(db)
      sendJson(res, 200, { ok: true })
    })
    return
  }

  if (req.url.startsWith('/stock-flows') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const flows = (db.stockFlows || []).filter((item) => item.account === account)
    sendJson(res, 200, { ok: true, stockFlows: flows })
    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Mock securities service running at http://localhost:${PORT}`)
})
