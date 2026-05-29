import {
  fetchAccountSummary,
  fetchFunds as fetchClientFunds,
  fetchHoldings as fetchClientHoldings,
  fetchOrders as fetchClientOrders,
  placeOrder as placeClientOrder,
  cancelOrder as cancelClientOrder,
  fetchFills as fetchClientFills,
  fetchCashFlows as fetchClientCashFlows,
  fetchStockFlows as fetchClientStockFlows,
  fetchAlerts as fetchClientAlerts,
  createAlert as createClientAlert,
  updateAlert as updateClientAlert,
  deleteAlert as deleteClientAlert,
  depositFunds as depositClientFunds,
  withdrawFunds as withdrawClientFunds,
  changeTradePassword as changeClientTradePassword,
  changeWithdrawPassword as changeClientWithdrawPassword,
  addLoginRecord as addClientLoginRecord,
  fetchLoginRecords as fetchClientLoginRecords,
  fetchNotifications as fetchClientNotifications,
  markNotificationRead,
  fetchWatchlist as fetchClientWatchlist,
  toggleWatchlist as toggleClientWatchlist,
  fetchPreferences as fetchClientPreferences,
  updatePreferences,
} from './clientApi'

export const fetchAccount = (account = 'admin') => fetchAccountSummary(account)

export const fetchFunds = (account = 'admin') => fetchClientFunds(account)

export const fetchHoldings = (account = 'admin') => fetchClientHoldings(account)

export const fetchOrders = (account = 'admin') => fetchClientOrders(account)

export const placeOrder = (payload: {
  account?: string
  symbol: string
  side: '买入' | '卖出'
  price: number
  quantity: number
  note?: string
}) => placeClientOrder(payload)

export const cancelOrder = (orderId: string) => cancelClientOrder(orderId)

export const fetchFills = (account = 'admin') => fetchClientFills(account)

export const fetchCashFlows = (account = 'admin') => fetchClientCashFlows(account)

export const fetchStockFlows = (account = 'admin') => fetchClientStockFlows(account)

export const depositFunds = (payload: { account?: string; amount: number }) =>
  depositClientFunds(payload)

export const withdrawFunds = (payload: { account?: string; amount: number; password?: string }) =>
  withdrawClientFunds(payload)

export const changeTradePassword = (payload: {
  account?: string
  currentPassword: string
  nextPassword: string
}) => changeClientTradePassword(payload)

export const changeWithdrawPassword = (payload: {
  account?: string
  currentPassword: string
  nextPassword: string
}) => changeClientWithdrawPassword(payload)

export const addLoginRecord = (payload: {
  account?: string
  time?: string
  method?: string
  device?: string
  status?: string
}) => addClientLoginRecord(payload)

export const fetchLoginRecords = (account = 'admin') => fetchClientLoginRecords(account)

export const fetchAlerts = (account = 'admin') => fetchClientAlerts(account)

export const createAlert = (payload: {
  account?: string
  symbol: string
  condition: string
  triggerPrice: string
}) => createClientAlert(payload)

export const updateAlert = (alertId: string, payload: Record<string, unknown>) =>
  updateClientAlert(alertId, payload)

export const deleteAlert = (alertId: string) => deleteClientAlert(alertId)

export const fetchNotifications = (account = 'admin') => fetchClientNotifications(account)

export const markNotification = (notificationId: string) => markNotificationRead(notificationId)

export const fetchWatchlist = (account = 'admin') => fetchClientWatchlist(account)

export const toggleWatchlist = (symbol: string, account?: string) =>
  toggleClientWatchlist(symbol, account)

export const fetchPreferences = (account = 'admin') => fetchClientPreferences(account)

export const updatePreferencesData = (payload: Record<string, unknown>) => updatePreferences(payload)
