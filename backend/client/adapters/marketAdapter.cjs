const fetchJson = async (url) => {
  const response = await fetch(url)
  const data = await response.json().catch(() => ({}))
  if (!response.ok || !data.ok) {
    const message = data.message || '行情服务请求失败'
    throw new Error(message)
  }
  return data
}

const resolveBase = () =>
  process.env.MARKET_SERVICE_BASE_URL || 'http://localhost:3024'

const getStocks = async (query, board) => {
  const params = new URLSearchParams()
  if (query) params.set('query', query)
  if (board) params.set('board', board)
  return fetchJson(`${resolveBase()}/stocks?${params.toString()}`)
}

const getStock = async (symbol) =>
  fetchJson(`${resolveBase()}/stocks?symbol=${encodeURIComponent(symbol)}`)

const getQuotes = async (symbols) => {
  const payload = await getStocks('', '')
  const list = payload.stocks || []
  if (!symbols || symbols.length === 0) {
    return { ok: true, asOf: payload.asOf, stocks: list }
  }
  return {
    ok: true,
    asOf: payload.asOf,
    stocks: list.filter((item) => symbols.includes(item.symbol)),
  }
}

module.exports = {
  getStocks,
  getStock,
  getQuotes,
}
