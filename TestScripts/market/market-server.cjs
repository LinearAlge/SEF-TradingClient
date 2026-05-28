const http = require('http')
const fs = require('fs')
const path = require('path')

const PORT = process.env.PORT || 3004
const DB_PATH = path.join(__dirname, 'market-db.json')

const DEFAULT_DB = {
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

const formatAsOf = () => {
  const now = new Date()
  const offsetMs = 8 * 60 * 60 * 1000
  const local = new Date(now.getTime() + offsetMs)
  return local.toISOString().replace('Z', '+08:00')
}

const applyPriceDrift = (price) => {
  const change = Math.random() * 0.008 - 0.004
  const next = price * (1 + change)
  return Math.max(0.01, Number(next.toFixed(2)))
}

const updateStock = (stock) => {
  const lastPrice = applyPriceDrift(stock.lastPrice)
  const bid = Number((lastPrice * 0.999).toFixed(2))
  const ask = Number((lastPrice * 1.001).toFixed(2))
  const volume = stock.volume + Math.floor(Math.random() * 4000 + 500)

  return {
    ...stock,
    lastPrice,
    bid,
    ask,
    volume,
    dayHigh: Math.max(stock.dayHigh, lastPrice),
    dayLow: Math.min(stock.dayLow, lastPrice),
    weekHigh: Math.max(stock.weekHigh, lastPrice),
    weekLow: Math.min(stock.weekLow, lastPrice),
    monthHigh: Math.max(stock.monthHigh, lastPrice),
    monthLow: Math.min(stock.monthLow, lastPrice),
  }
}

const updateMarketSnapshot = () => {
  const db = loadDb()
  if (!db.stocks || db.stocks.length === 0) {
    return
  }

  db.asOf = formatAsOf()
  db.stocks = db.stocks.map(updateStock)
  saveDb(db)
}

const filterStocks = (stocks, query, board) => {
  const normalizedQuery = (query || '').trim()
  const normalizedBoard = (board || '').trim()

  return stocks.filter((stock) => {
    const matchesBoard = !normalizedBoard || stock.board === normalizedBoard
    if (!normalizedQuery) {
      return matchesBoard
    }

    const text = `${stock.symbol}${stock.name}`.toLowerCase()
    return matchesBoard && text.includes(normalizedQuery.toLowerCase())
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

  if (req.url.startsWith('/stocks') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const query = url.searchParams.get('query') || ''
    const board = url.searchParams.get('board') || ''
    const symbol = url.searchParams.get('symbol') || ''

    const db = loadDb()
    if (symbol) {
      const stock = db.stocks.find((item) => item.symbol === symbol)
      if (!stock) {
        sendJson(res, 404, { ok: false, message: '股票不存在' })
        return
      }

      sendJson(res, 200, {
        ok: true,
        asOf: db.asOf,
        stock,
      })
      return
    }

    const filtered = filterStocks(db.stocks || [], query, board)
    sendJson(res, 200, {
      ok: true,
      asOf: db.asOf,
      stocks: filtered,
    })
    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Market mock server running at http://localhost:${PORT}`)
})

updateMarketSnapshot()
setInterval(updateMarketSnapshot, 5000)
