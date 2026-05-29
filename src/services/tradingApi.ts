const BASE_URL = 'http://localhost:3005'

const requestJson = async (path: string, options?: RequestInit) => {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok || !data.ok) {
    const message = data.message || '请求失败'
    throw new Error(message)
  }
  return data
}

export const fetchAccount = (account = 'admin') =>
  requestJson(`/account?account=${encodeURIComponent(account)}`)

export const fetchFunds = (account = 'admin') =>
  requestJson(`/funds?account=${encodeURIComponent(account)}`)

export const fetchHoldings = (account = 'admin') =>
  requestJson(`/holdings?account=${encodeURIComponent(account)}`)

export const fetchOrders = (account = 'admin') =>
  requestJson(`/orders?account=${encodeURIComponent(account)}`)

export const placeOrder = (payload: {
  account?: string
  symbol: string
  side: '买入' | '卖出'
  price: number
  quantity: number
  note?: string
}) =>
  requestJson('/orders', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const cancelOrder = (orderId: string) =>
  requestJson(`/orders/${encodeURIComponent(orderId)}/cancel`, {
    method: 'POST',
  })

export const fetchFills = (account = 'admin') =>
  requestJson(`/fills?account=${encodeURIComponent(account)}`)

export const fetchCashFlows = (account = 'admin') =>
  requestJson(`/cash-flows?account=${encodeURIComponent(account)}`)

export const fetchStockFlows = (account = 'admin') =>
  requestJson(`/stock-flows?account=${encodeURIComponent(account)}`)

export const fetchAlerts = (account = 'admin') =>
  requestJson(`/alerts?account=${encodeURIComponent(account)}`)

export const createAlert = (payload: {
  account?: string
  symbol: string
  condition: string
  triggerPrice: string
}) =>
  requestJson('/alerts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const updateAlert = (alertId: string, payload: Record<string, unknown>) =>
  requestJson(`/alerts/${encodeURIComponent(alertId)}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })

export const deleteAlert = (alertId: string) =>
  requestJson(`/alerts/${encodeURIComponent(alertId)}`, {
    method: 'DELETE',
  })

export const depositFunds = (payload: { account?: string; amount: number }) =>
  requestJson('/funds/deposit', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const withdrawFunds = (payload: { account?: string; amount: number; password?: string }) =>
  requestJson('/funds/withdraw', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const changeTradePassword = (payload: {
  account?: string
  currentPassword: string
  nextPassword: string
}) =>
  requestJson('/passwords/trade', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const changeWithdrawPassword = (payload: {
  account?: string
  currentPassword: string
  nextPassword: string
}) =>
  requestJson('/passwords/withdraw', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const addLoginRecord = (payload: {
  account?: string
  time?: string
  method?: string
  device?: string
  status?: string
}) =>
  requestJson('/login-records', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const fetchLoginRecords = (account = 'admin') =>
  requestJson(`/login-records?account=${encodeURIComponent(account)}`)
