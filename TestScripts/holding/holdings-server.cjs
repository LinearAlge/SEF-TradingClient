const http = require('http')
const fs = require('fs')
const path = require('path')

const PORT = process.env.PORT || 3002
const DB_PATH = path.join(__dirname, '..', 'data', 'trading-db.json')

const DEFAULT_DB = {
  accounts: {},
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
  const change = Math.random() * 0.01 - 0.005
  const next = price * (1 + change)
  return Math.max(0.01, Number(next.toFixed(2)))
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

const buildHoldingSummary = (positions = []) => {
  return positions.map((position) => {
    const totalShares = position.lots.reduce((sum, lot) => sum + lot.shares, 0)
    const totalCost = position.lots.reduce((sum, lot) => sum + lot.price * lot.shares, 0)
    const costPrice = totalShares ? totalCost / totalShares : 0
    const marketValue = totalShares * position.lastPrice
    const pnlAmount = marketValue - totalCost
    const pnlRate = totalCost ? pnlAmount / totalCost : 0

    return {
      symbol: position.symbol,
      name: position.name,
      shares: totalShares,
      costPrice,
      lastPrice: position.lastPrice,
      pnlAmount,
      pnlRate,
    }
  })
}

const updateRecordSnapshot = (record) => {
  record.asOf = formatAsOf()
  record.positions = (record.positions || []).map((position) => ({
    ...position,
    lastPrice: applyPriceDrift(position.lastPrice),
  }))
}

const updateAllRecords = () => {
  const db = loadDb()
  const accounts = db.accounts || {}
  const records = Object.values(accounts)
  if (records.length === 0) {
    return
  }

  records.forEach((record) => {
    updateRecordSnapshot(record)
  })

  saveDb(db)
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

  if (req.url.startsWith('/holdings') && req.method === 'GET') {
    const url = new URL(req.url, `http://${req.headers.host}`)
    const account = url.searchParams.get('account') || 'admin'
    const db = loadDb()
    const record = db.accounts?.[account]

    if (!record) {
      sendJson(res, 404, { ok: false, message: '账户不存在' })
      return
    }

    const holdings = buildHoldingSummary(record.positions || [])
    const totalMarketValue = holdings.reduce((sum, item) => sum + item.lastPrice * item.shares, 0)

    sendJson(res, 200, {
      ok: true,
      account,
      securitiesAccountId: record.securitiesAccountId,
      asOf: record.asOf,
      totalMarketValue,
      holdings,
    })
    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Holdings mock server running at http://localhost:${PORT}`)
})

updateAllRecords()
setInterval(updateAllRecords, 5000)
