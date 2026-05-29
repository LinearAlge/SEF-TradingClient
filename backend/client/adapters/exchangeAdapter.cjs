const fetchJson = async (url, options) => {
  const response = await fetch(url, options)
  const data = await response.json().catch(() => ({}))
  if (!response.ok || !data.ok) {
    const message = data.message || '交易服务请求失败'
    throw new Error(message)
  }
  return data
}

const resolveBase = () =>
  process.env.EXCHANGE_SERVICE_BASE_URL || 'http://localhost:3023'

const placeOrder = async (payload) =>
  fetchJson(`${resolveBase()}/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

const cancelOrder = async (orderId) =>
  fetchJson(`${resolveBase()}/orders/${encodeURIComponent(orderId)}/cancel`, {
    method: 'POST',
  })

const getOrders = async (account) =>
  fetchJson(`${resolveBase()}/orders?account=${encodeURIComponent(account)}`)

const getFills = async (account) =>
  fetchJson(`${resolveBase()}/fills?account=${encodeURIComponent(account)}`)

module.exports = {
  placeOrder,
  cancelOrder,
  getOrders,
  getFills,
}
