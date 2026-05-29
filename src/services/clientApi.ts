const BASE_URL = import.meta.env.VITE_CLIENT_API_BASE || 'http://localhost:3010/api'

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

export const authLogin = async (payload: { account: string; password: string }) => {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok || !data.ok) {
    return {
      ok: false,
      status: response.status,
      action: data.action,
      message: data.message || '登录失败，请检查账号或密码',
    }
  }
  return data
}

export const authEnroll = (payload: { account: string; publicKey: unknown }) =>
  requestJson('/auth/enroll', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const authVerify = (payload: { account: string; signature: string }) =>
  requestJson('/auth/verify', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const authRebind = (payload: {
  account: string
  password: string
  phone: string
  idNumber: string
}) =>
  requestJson('/auth/rebind', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const applyClientAccess = (payload: {
  account: string
  password: string
  name?: string
  phone: string
  idNumber?: string
}) =>
  requestJson('/client/applications', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const fetchAuthProfile = (account?: string) =>
  requestJson(`/auth/me?account=${encodeURIComponent(account || 'admin')}`)

export const fetchAccountSummary = (account?: string) =>
  requestJson(`/account/summary?account=${encodeURIComponent(account || 'admin')}`)

export const fetchFunds = (account?: string) =>
  requestJson(`/account/funds?account=${encodeURIComponent(account || 'admin')}`)

export const fetchHoldings = (account?: string) =>
  requestJson(`/account/holdings?account=${encodeURIComponent(account || 'admin')}`)

export const fetchCashFlows = (account?: string) =>
  requestJson(`/account/cash-flows?account=${encodeURIComponent(account || 'admin')}`)

export const fetchStockFlows = (account?: string) =>
  requestJson(`/account/stock-flows?account=${encodeURIComponent(account || 'admin')}`)

export const depositFunds = (payload: { account?: string; amount: number }) =>
  requestJson('/account/funds/deposit', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const withdrawFunds = (payload: { account?: string; amount: number; password?: string }) =>
  requestJson('/account/funds/withdraw', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const changeTradePassword = (payload: {
  account?: string
  currentPassword: string
  nextPassword: string
}) =>
  requestJson('/account/passwords/trade', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const changeWithdrawPassword = (payload: {
  account?: string
  currentPassword: string
  nextPassword: string
}) =>
  requestJson('/account/passwords/withdraw', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const fetchStocks = (params: { query?: string; board?: string }) => {
  const query = new URLSearchParams()
  if (params.query) query.set('query', params.query)
  if (params.board) query.set('board', params.board)
  return requestJson(`/market/stocks?${query.toString()}`)
}

export const fetchStock = (symbol: string) =>
  requestJson(`/market/stocks?symbol=${encodeURIComponent(symbol)}`)

export const fetchQuotes = (symbols?: string[]) => {
  const query = symbols && symbols.length > 0 ? `?symbols=${symbols.join(',')}` : ''
  return requestJson(`/market/quotes${query}`)
}

export const placeOrder = (payload: {
  account?: string
  symbol: string
  side: '买入' | '卖出'
  price: number
  quantity: number
  note?: string
}) =>
  requestJson('/trade/orders', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const fetchOrders = (account?: string) =>
  requestJson(`/trade/orders?account=${encodeURIComponent(account || 'admin')}`)

export const cancelOrder = (orderId: string) =>
  requestJson(`/trade/orders/${encodeURIComponent(orderId)}/cancel`, {
    method: 'POST',
  })

export const fetchFills = (account?: string) =>
  requestJson(`/trade/fills?account=${encodeURIComponent(account || 'admin')}`)

export const fetchAlerts = (account?: string) =>
  requestJson(`/client/alerts?account=${encodeURIComponent(account || 'admin')}`)

export const createAlert = (payload: {
  account?: string
  symbol: string
  condition: string
  triggerPrice: string
}) =>
  requestJson('/client/alerts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const updateAlert = (alertId: string, payload: Record<string, unknown>) =>
  requestJson(`/client/alerts/${encodeURIComponent(alertId)}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })

export const deleteAlert = (alertId: string) =>
  requestJson(`/client/alerts/${encodeURIComponent(alertId)}`, {
    method: 'DELETE',
  })

export const fetchNotifications = (account?: string) =>
  requestJson(`/client/notifications?account=${encodeURIComponent(account || 'admin')}`)

export const markNotificationRead = (notificationId: string) =>
  requestJson(`/client/notifications/${encodeURIComponent(notificationId)}/read`, {
    method: 'PATCH',
  })

export const fetchWatchlist = (account?: string) =>
  requestJson(`/client/watchlist?account=${encodeURIComponent(account || 'admin')}`)

export const toggleWatchlist = (symbol: string, account?: string) =>
  requestJson(
    `/client/watchlist/${encodeURIComponent(symbol)}/toggle?account=${encodeURIComponent(
      account || 'admin',
    )}`,
    {
      method: 'POST',
    },
  )

export const fetchPreferences = (account?: string) =>
  requestJson(`/client/preferences?account=${encodeURIComponent(account || 'admin')}`)

export const updatePreferences = (payload: Record<string, unknown>) =>
  requestJson('/client/preferences', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })

export const addLoginRecord = (payload: {
  account?: string
  time?: string
  method?: string
  device?: string
  status?: string
}) =>
  requestJson('/client/login-records', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const fetchLoginRecords = (account?: string) =>
  requestJson(`/client/login-records?account=${encodeURIComponent(account || 'admin')}`)
