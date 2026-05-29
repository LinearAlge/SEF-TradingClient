const fetchJson = async (url, options) => {
  const response = await fetch(url, options)
  const data = await response.json().catch(() => ({}))
  if (!response.ok || !data.ok) {
    const message = data.message || '证券服务请求失败'
    throw new Error(message)
  }
  return data
}

const resolveBase = () =>
  process.env.SECURITIES_SERVICE_BASE_URL || 'http://localhost:3022'

const getHoldings = async (account) =>
  fetchJson(`${resolveBase()}/holdings?account=${encodeURIComponent(account)}`)

const getStockFlows = async (account) =>
  fetchJson(`${resolveBase()}/stock-flows?account=${encodeURIComponent(account)}`)

const applyTradeFill = async (payload) =>
  fetchJson(`${resolveBase()}/positions/apply-fill`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

module.exports = {
  getHoldings,
  getStockFlows,
  applyTradeFill,
}
