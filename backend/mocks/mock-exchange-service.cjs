const http = require('http')
const fs = require('fs')
const path = require('path')

const PORT = process.env.PORT || 3023
const DB_PATH = path.join(__dirname, 'data', 'mock-exchange-db.json')
const MARKET_DB_PATH = path.join(__dirname, 'data', 'mock-market-db.json')

const DEFAULT_DB = {
  accounts: {},
  orders: [],
  fills: [],
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

const formatTime = () =>
  new Date().toLocaleString('zh-CN', {
    hour12: false,
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

const applyMatching = (order, marketIndex) => {
  const stock = marketIndex[order.symbol]
  if (!shouldFillOrder(order, stock)) {
    return null
  }

  const fillPrice = resolveFillPrice(order, stock)
  const remaining = order.quantity - order.filledQuantity
  const fillQty = order.quantity > 500 ? Math.min(500, remaining) : remaining

  if (fillQty <= 0) return null

  applyFillToOrder(order, fillPrice, fillQty)
  return createFill({
    orderId: order.id,
    symbol: order.symbol,
    side: order.side,
    price: fillPrice,
    quantity: fillQty,
  })
}

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

  if (req.url.startsWith('/orders') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const orders = (db.orders || []).filter((order) => order.account === account)
    sendJson(res, 200, { ok: true, orders })
    return
  }

  if (req.url === '/orders' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const db = loadDb()
      const order = createOrder(payload)
      db.orders.unshift(order)

      const marketIndex = buildMarketIndex(loadMarketDb())
      const fill = applyMatching(order, marketIndex)
      const fills = fill ? [fill] : []
      if (fill) {
        db.fills.unshift(fill)
      }

      saveDb(db)
      sendJson(res, 200, { ok: true, order, fills })
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

    order.status = '已撤单'
    saveDb(db)
    sendJson(res, 200, { ok: true, order })
    return
  }

  if (req.url.startsWith('/fills') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const fills = (db.fills || []).filter((item) => {
      const order = (db.orders || []).find((orderItem) => orderItem.id === item.orderId)
      return order?.account === account
    })

    sendJson(res, 200, { ok: true, fills })
    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Mock exchange service running at http://localhost:${PORT}`)
})
