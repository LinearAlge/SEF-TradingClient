const http = require('http')
const fs = require('fs')
const path = require('path')

const PORT = process.env.PORT || 3003
const DB_PATH = path.join(__dirname, '..', 'data', 'trading-db.json')
const MARKET_DB_PATH = path.join(__dirname, '..', 'market', 'market-db.json')

const DEFAULT_DB = {
  accounts: {},
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

const formatAsOf = () => {
  const now = new Date()
  const offsetMs = 8 * 60 * 60 * 1000
  const local = new Date(now.getTime() + offsetMs)
  return local.toISOString().replace('Z', '+08:00')
}

const calculateMarketValue = (positions = [], marketIndex = {}) => {
  return positions.reduce((sum, position) => {
    const totalShares = (position.lots || []).reduce((lotSum, lot) => lotSum + lot.shares, 0)
    const lastPrice = Number(marketIndex[position.symbol]?.lastPrice ?? position.lastPrice ?? 0)
    return sum + totalShares * lastPrice
  }, 0)
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
    const available = Number(balances.available ?? record.available ?? 0)
    const frozen = Number(balances.frozen ?? record.frozen ?? 0)
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

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Funds mock server running at http://localhost:${PORT}`)
})
