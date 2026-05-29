const http = require('http')
const fs = require('fs')
const path = require('path')

const PORT = process.env.PORT || 3005
const DB_PATH = path.join(__dirname, 'trading-db.json')
const MARKET_DB_PATH = path.join(__dirname, '..', 'market', 'market-db.json')

const DEFAULT_DB = {
  accounts: {},
  orders: [],
  fills: [],
  cashFlows: [],
  stockFlows: [],
  alerts: [],
  loginRecords: [],
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
    'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
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

const round2 = (value) => Number(value.toFixed(2))

const toNumber = (value, fallback = 0) => {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

const formatTime = () =>
  new Date().toLocaleString('zh-CN', {
    hour12: false,
  })

const buildHoldingSummary = (positions = [], marketIndex = {}) => {
  return positions.map((position) => {
    const stock = marketIndex[position.symbol]
    const name = stock?.name || position.name || position.symbol
    const lastPrice = Number(stock?.lastPrice ?? position.lastPrice ?? 0)
    const totalShares = (position.lots || []).reduce((sum, lot) => sum + lot.shares, 0)
    const totalCost = (position.lots || []).reduce((sum, lot) => sum + lot.price * lot.shares, 0)
    const costPrice = totalShares ? totalCost / totalShares : 0
    const marketValue = totalShares * lastPrice
    const pnlAmount = marketValue - totalCost
    const pnlRate = totalCost ? pnlAmount / totalCost : 0

    return {
      symbol: position.symbol,
      name,
      shares: totalShares,
      costPrice,
      lastPrice,
      pnlAmount,
      pnlRate,
    }
  })
}

const getAccountRecord = (db, account) => db.accounts?.[account]

const calculateMarketValue = (positions = [], marketIndex = {}) => {
  return positions.reduce((sum, position) => {
    const totalShares = (position.lots || []).reduce((lotSum, lot) => lotSum + lot.shares, 0)
    const lastPrice = Number(marketIndex[position.symbol]?.lastPrice ?? position.lastPrice ?? 0)
    return sum + totalShares * lastPrice
  }, 0)
}

const calculateFrozenShares = (db, account, symbol) => {
  return (db.orders || []).reduce((sum, order) => {
    if (order.account !== account) return sum
    if (order.symbol !== symbol) return sum
    if (order.side !== '卖出') return sum
    if (!['未成交', '部分成交'].includes(order.status)) return sum
    const unfilled = Math.max(0, order.quantity - order.filledQuantity)
    return sum + unfilled
  }, 0)
}

const getAvailableShares = (db, account, symbol, positionShares) => {
  const frozen = calculateFrozenShares(db, account, symbol)
  return Math.max(0, positionShares - frozen)
}

const ensureAccountExists = (db, account, res) => {
  const record = getAccountRecord(db, account)
  if (!record) {
    sendJson(res, 404, { ok: false, message: '账户不存在' })
    return null
  }
  return record
}

const buildOrderSummary = (order, marketIndex) => {
  const stock = marketIndex[order.symbol]
  return {
    ...order,
    name: order.name || stock?.name || order.symbol,
  }
}

const createCashFlow = (payload) => ({
  id: `CASH-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
  time: formatTime(),
  status: '已完成',
  ...payload,
})

const createStockFlow = (payload) => ({
  id: `STK-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
  time: formatTime(),
  status: '已完成',
  ...payload,
})

const createFill = (payload) => ({
  id: `FILL-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
  createdAt: formatTime(),
  ...payload,
})

const createOrder = (payload) => ({
  id: `ORD-${Date.now()}`,
  createdAt: formatTime(),
  filledQuantity: 0,
  avgPrice: 0,
  status: '未成交',
  ...payload,
})

const applyFillToOrder = (order, fillPrice, fillQty) => {
  const totalFilled = order.filledQuantity + fillQty
  const totalAmount = order.avgPrice * order.filledQuantity + fillPrice * fillQty
  const avgPrice = totalFilled ? totalAmount / totalFilled : 0
  order.filledQuantity = totalFilled
  order.avgPrice = round2(avgPrice)
  if (order.filledQuantity >= order.quantity) {
    order.status = '已成交'
  } else {
    order.status = '部分成交'
  }
}

const applyBuyFill = (db, accountRecord, order, fillPrice, fillQty, marketIndex) => {
  const amount = fillPrice * fillQty
  const balances = accountRecord.balances
  balances.frozen = round2(balances.frozen - amount)

  const position = accountRecord.positions.find((item) => item.symbol === order.symbol)
  const newLot = { price: fillPrice, shares: fillQty }
  if (position) {
    position.lots.push(newLot)
  } else {
    accountRecord.positions.push({ symbol: order.symbol, lots: [newLot] })
  }

  db.fills.unshift(
    createFill({
      orderId: order.id,
      symbol: order.symbol,
      side: order.side,
      price: fillPrice,
      quantity: fillQty,
    }),
  )

  db.cashFlows.unshift(
    createCashFlow({
      type: '买入成交',
      amount: `-${round2(amount).toFixed(2)}`,
      symbol: order.symbol,
    }),
  )

  db.stockFlows.unshift(
    createStockFlow({
      type: '买入成交',
      symbol: order.symbol,
      qty: `${fillQty}`,
    }),
  )

  accountRecord.asOf = formatAsOf()
}

const applySellFill = (db, accountRecord, order, fillPrice, fillQty, marketIndex) => {
  const amount = fillPrice * fillQty
  const balances = accountRecord.balances
  balances.available = round2(balances.available + amount)

  const position = accountRecord.positions.find((item) => item.symbol === order.symbol)
  if (position) {
    let remaining = fillQty
    position.lots = position.lots
      .map((lot) => {
        if (remaining <= 0) return lot
        const deduct = Math.min(lot.shares, remaining)
        remaining -= deduct
        return { ...lot, shares: lot.shares - deduct }
      })
      .filter((lot) => lot.shares > 0)
  }

  db.fills.unshift(
    createFill({
      orderId: order.id,
      symbol: order.symbol,
      side: order.side,
      price: fillPrice,
      quantity: fillQty,
    }),
  )

  db.cashFlows.unshift(
    createCashFlow({
      type: '卖出成交',
      amount: `+${round2(amount).toFixed(2)}`,
      symbol: order.symbol,
    }),
  )

  db.stockFlows.unshift(
    createStockFlow({
      type: '卖出成交',
      symbol: order.symbol,
      qty: `-${fillQty}`,
    }),
  )

  accountRecord.asOf = formatAsOf()
}

const resolveFillPrice = (order, stock) => {
  if (!stock) return order.price
  if (order.side === '买入') {
    return Number(stock.ask || stock.lastPrice || order.price)
  }
  return Number(stock.bid || stock.lastPrice || order.price)
}

const shouldFillOrder = (order, stock) => {
  if (!stock) return false
  if (order.side === '买入') {
    return order.price >= Number(stock.ask || stock.lastPrice)
  }
  return order.price <= Number(stock.bid || stock.lastPrice)
}

const applyMatching = (db, accountRecord, order, marketIndex) => {
  const stock = marketIndex[order.symbol]
  if (!shouldFillOrder(order, stock)) {
    return
  }

  const fillPrice = resolveFillPrice(order, stock)
  const remaining = order.quantity - order.filledQuantity
  const fillQty = order.quantity > 500 ? Math.min(500, remaining) : remaining

  if (fillQty <= 0) return

  if (order.side === '买入') {
    applyBuyFill(db, accountRecord, order, fillPrice, fillQty, marketIndex)
  } else {
    applySellFill(db, accountRecord, order, fillPrice, fillQty, marketIndex)
  }

  applyFillToOrder(order, fillPrice, fillQty)
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
    })
    res.end()
    return
  }

  if (req.url === '/health' && req.method === 'GET') {
    sendJson(res, 200, { ok: true })
    return
  }

  if (req.url.startsWith('/account') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const marketDb = loadMarketDb()
    const marketIndex = buildMarketIndex(marketDb)
    const marketValue = calculateMarketValue(record.positions || [], marketIndex)
    const balances = record.balances || { available: 0, frozen: 0 }

    sendJson(res, 200, {
      ok: true,
      account,
      fundAccountId: record.fundAccountId,
      securitiesAccountId: record.securitiesAccountId,
      currency: record.currency,
      available: balances.available,
      frozen: balances.frozen,
      marketValue,
      totalEquity: round2(balances.available + balances.frozen + marketValue),
      updatedAt: record.asOf || formatAsOf(),
    })
    return
  }

  if (req.url.startsWith('/funds') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const marketDb = loadMarketDb()
    const marketIndex = buildMarketIndex(marketDb)
    const marketValue = calculateMarketValue(record.positions || [], marketIndex)
    const balances = record.balances || { available: 0, frozen: 0 }

    sendJson(res, 200, {
      ok: true,
      account,
      fundAccountId: record.fundAccountId,
      currency: record.currency,
      available: balances.available,
      frozen: balances.frozen,
      marketValue,
      totalEquity: round2(balances.available + balances.frozen + marketValue),
      updatedAt: record.asOf || formatAsOf(),
    })
    return
  }

  if (req.url.startsWith('/holdings') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const marketDb = loadMarketDb()
    const marketIndex = buildMarketIndex(marketDb)
    const holdings = buildHoldingSummary(record.positions || [], marketIndex).map((item) => {
      const frozenShares = calculateFrozenShares(db, account, item.symbol)
      const availableShares = Math.max(0, item.shares - frozenShares)
      return { ...item, frozenShares, availableShares }
    })

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

  if (req.url.startsWith('/orders') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const marketIndex = buildMarketIndex(loadMarketDb())
    const orders = (db.orders || [])
      .filter((order) => order.account === account)
      .map((order) => buildOrderSummary(order, marketIndex))

    sendJson(res, 200, {
      ok: true,
      account,
      orders,
    })
    return
  }

  if (req.url === '/orders' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const db = loadDb()
      const record = ensureAccountExists(db, account, res)
      if (!record) return

      const marketDb = loadMarketDb()
      const marketIndex = buildMarketIndex(marketDb)
      const stock = marketIndex[payload.symbol]
      if (!stock) {
        sendJson(res, 400, { ok: false, message: '股票不存在' })
        return
      }

      const side = payload.side === '卖出' ? '卖出' : '买入'
      const price = toNumber(payload.price)
      const quantity = Math.floor(toNumber(payload.quantity))

      if (!price || price <= 0) {
        sendJson(res, 400, { ok: false, message: '价格必须大于 0' })
        return
      }
      if (!quantity || quantity <= 0) {
        sendJson(res, 400, { ok: false, message: '数量必须大于 0' })
        return
      }

      const limitUp = stock.lastPrice * 1.1
      const limitDown = stock.lastPrice * 0.9
      if (price > limitUp || price < limitDown) {
        sendJson(res, 400, { ok: false, message: '委托价格超出涨跌停范围' })
        return
      }

      if (side === '买入') {
        const amount = price * quantity
        if (amount > record.balances.available) {
          sendJson(res, 400, { ok: false, message: '委托金额超过可用资金' })
          return
        }
      } else {
        const position = record.positions.find((item) => item.symbol === payload.symbol)
        if (!position) {
          sendJson(res, 400, { ok: false, message: '持仓不足' })
          return
        }
        const totalShares = position.lots.reduce((sum, lot) => sum + lot.shares, 0)
        const availableShares = getAvailableShares(db, account, payload.symbol, totalShares)
        if (quantity > availableShares) {
          sendJson(res, 400, { ok: false, message: '委托数量超过可卖数量' })
          return
        }
      }

      const order = createOrder({
        account,
        symbol: payload.symbol,
        name: stock.name,
        side,
        price: round2(price),
        quantity,
        note: payload.note || '',
      })

      db.orders.unshift(order)

      if (side === '买入') {
        const amount = round2(order.price * order.quantity)
        record.balances.available = round2(record.balances.available - amount)
        record.balances.frozen = round2(record.balances.frozen + amount)
        db.cashFlows.unshift(
          createCashFlow({
            type: '买入委托冻结',
            amount: `-${amount.toFixed(2)}`,
            symbol: order.symbol,
          }),
        )
      } else {
        db.stockFlows.unshift(
          createStockFlow({
            type: '卖出委托冻结',
            symbol: order.symbol,
            qty: `${order.quantity}`,
          }),
        )
      }

      applyMatching(db, record, order, marketIndex)

      saveDb(db)
      sendJson(res, 200, { ok: true, order })
    })
    return
  }

  if (req.url.startsWith('/orders/') && req.method === 'POST') {
    const match = req.url.match(/\/orders\/(.+)\/cancel/)
    if (!match) {
      sendJson(res, 404, { ok: false, message: 'Not found' })
      return
    }

    const orderId = match[1]
    const db = loadDb()
    const order = (db.orders || []).find((item) => item.id === orderId)
    if (!order) {
      sendJson(res, 404, { ok: false, message: '委托不存在' })
      return
    }

    if (!['未成交', '部分成交'].includes(order.status)) {
      sendJson(res, 400, { ok: false, message: '当前委托不可撤销' })
      return
    }

    const record = ensureAccountExists(db, order.account, res)
    if (!record) return

    const unfilled = Math.max(0, order.quantity - order.filledQuantity)

    if (order.side === '买入') {
      const releaseAmount = round2(order.price * unfilled)
      record.balances.available = round2(record.balances.available + releaseAmount)
      record.balances.frozen = round2(record.balances.frozen - releaseAmount)
      db.cashFlows.unshift(
        createCashFlow({
          type: '撤单解冻',
          amount: `+${releaseAmount.toFixed(2)}`,
          symbol: order.symbol,
        }),
      )
    } else {
      db.stockFlows.unshift(
        createStockFlow({
          type: '撤单解冻',
          symbol: order.symbol,
          qty: `${unfilled}`,
        }),
      )
    }

    order.status = '已撤单'
    saveDb(db)
    sendJson(res, 200, { ok: true, order })
    return
  }

  if (req.url.startsWith('/fills') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const fills = (db.fills || []).filter((item) => {
      const order = (db.orders || []).find((orderItem) => orderItem.id === item.orderId)
      return order?.account === account
    })

    sendJson(res, 200, { ok: true, account, fills })
    return
  }

  if (req.url.startsWith('/cash-flows') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const cashFlows = (db.cashFlows || []).filter((item) => item.account === account || !item.account)
    sendJson(res, 200, { ok: true, account, cashFlows })
    return
  }

  if (req.url.startsWith('/stock-flows') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const stockFlows = (db.stockFlows || []).filter((item) => item.account === account || !item.account)
    sendJson(res, 200, { ok: true, account, stockFlows })
    return
  }

  if (req.url.startsWith('/alerts') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const alerts = (db.alerts || []).filter((item) => item.account === account)
    sendJson(res, 200, { ok: true, account, alerts })
    return
  }

  if (req.url === '/alerts' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const db = loadDb()
      const record = ensureAccountExists(db, account, res)
      if (!record) return

      const symbol = (payload.symbol || '').trim()
      if (!symbol) {
        sendJson(res, 400, { ok: false, message: '股票代码不能为空' })
        return
      }

      const alert = {
        id: `ALT-${Date.now()}`,
        account,
        symbol,
        condition: payload.condition || '高于',
        triggerPrice: String(payload.triggerPrice || payload.price || ''),
        currentPrice: '--',
        status: '监控中',
        lastTriggered: '--',
        createdAt: formatTime(),
      }
      db.alerts.unshift(alert)
      saveDb(db)
      sendJson(res, 200, { ok: true, alert })
    })
    return
  }

  if (req.url.startsWith('/alerts/') && req.method === 'PATCH') {
    const match = req.url.match(/\/alerts\/(.+)/)
    if (!match) {
      sendJson(res, 404, { ok: false, message: 'Not found' })
      return
    }
    const alertId = match[1]

    parseJsonBody(req, res, (payload) => {
      const db = loadDb()
      const alert = (db.alerts || []).find((item) => item.id === alertId)
      if (!alert) {
        sendJson(res, 404, { ok: false, message: '提醒不存在' })
        return
      }

      Object.assign(alert, payload, { updatedAt: formatTime() })
      saveDb(db)
      sendJson(res, 200, { ok: true, alert })
    })
    return
  }

  if (req.url.startsWith('/alerts/') && req.method === 'DELETE') {
    const match = req.url.match(/\/alerts\/(.+)/)
    if (!match) {
      sendJson(res, 404, { ok: false, message: 'Not found' })
      return
    }
    const alertId = match[1]
    const db = loadDb()
    const next = (db.alerts || []).filter((item) => item.id !== alertId)
    db.alerts = next
    saveDb(db)
    sendJson(res, 200, { ok: true })
    return
  }

  if (req.url === '/funds/deposit' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const amount = toNumber(payload.amount)
      if (!amount || amount <= 0) {
        sendJson(res, 400, { ok: false, message: '存款金额必须大于 0' })
        return
      }

      const db = loadDb()
      const record = ensureAccountExists(db, account, res)
      if (!record) return

      record.balances.available = round2(record.balances.available + amount)
      db.cashFlows.unshift(
        createCashFlow({
          type: '入金',
          amount: `+${round2(amount).toFixed(2)}`,
          symbol: payload.symbol || '',
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
      const amount = toNumber(payload.amount)
      const password = payload.password
      if (!amount || amount <= 0) {
        sendJson(res, 400, { ok: false, message: '取款金额必须大于 0' })
        return
      }

      const db = loadDb()
      const record = ensureAccountExists(db, account, res)
      if (!record) return

      const storedPassword = db.passwords?.[account]?.withdraw
      if (storedPassword && password && storedPassword !== password) {
        sendJson(res, 400, { ok: false, message: '取款密码错误' })
        return
      }

      if (amount > record.balances.available) {
        sendJson(res, 400, { ok: false, message: '取款金额超过可用资金' })
        return
      }

      record.balances.available = round2(record.balances.available - amount)
      db.cashFlows.unshift(
        createCashFlow({
          type: '出金',
          amount: `-${round2(amount).toFixed(2)}`,
          symbol: payload.symbol || '',
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

  if (req.url === '/login-records' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const db = loadDb()
      if (!db.accounts?.[account]) {
        sendJson(res, 404, { ok: false, message: '账户不存在' })
        return
      }

      const record = {
        id: `LOG-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
        account,
        time: payload.time || formatTime(),
        method: payload.method || '密码登录',
        device: payload.device || '未知',
        status: payload.status || '成功',
      }
      db.loginRecords.unshift(record)
      saveDb(db)
      sendJson(res, 200, { ok: true, record })
    })
    return
  }

  if (req.url.startsWith('/login-records') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = ensureAccountExists(db, account, res)
    if (!record) return

    const items = (db.loginRecords || []).filter((item) => item.account === account)
    sendJson(res, 200, { ok: true, account, records: items })
    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Trading mock server running at http://localhost:${PORT}`)
})
