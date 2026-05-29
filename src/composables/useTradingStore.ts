import { computed, reactive, readonly } from 'vue'
import {
  addLoginRecord,
  cancelOrder as apiCancelOrder,
  changeTradePassword,
  changeWithdrawPassword,
  createAlert as apiCreateAlert,
  deleteAlert as apiDeleteAlert,
  depositFunds,
  fetchAccount,
  fetchAlerts,
  fetchCashFlows,
  fetchFills,
  fetchFunds,
  fetchHoldings,
  fetchLoginRecords,
  fetchOrders,
  fetchStockFlows,
  placeOrder as apiPlaceOrder,
  updateAlert as apiUpdateAlert,
  withdrawFunds,
} from '../services/tradingApi'

type OrderStatus = '未成交' | '部分成交' | '已成交' | '已撤单' | '已过期' | '已拒绝'

type AlertStatus = '监控中' | '已暂停' | '已触发'

type FundsSnapshot = {
  available: number
  frozen: number
  marketValue: number
  totalEquity: number
  updatedAt?: string
}

type HoldingItem = {
  symbol: string
  name: string
  shares: number
  availableShares?: number
  frozenShares?: number
  costPrice: number
  lastPrice: number
  pnlAmount: number
  pnlRate: number
}

type OrderItem = {
  id: string
  createdAt: string
  symbol: string
  name?: string
  side: '买入' | '卖出'
  price: number
  quantity: number
  filledQuantity: number
  avgPrice?: number
  status: OrderStatus
}

type FillItem = {
  id: string
  createdAt: string
  orderId: string
  symbol: string
  side: '买入' | '卖出'
  price: number
  quantity: number
}

type AlertItem = {
  id: string
  symbol: string
  condition: string
  currentPrice: string
  triggerPrice: string
  status: AlertStatus
  lastTriggered: string
}

type CashFlowItem = {
  id: string
  time: string
  type: string
  amount: string
  status: string
  symbol?: string
}

type StockFlowItem = {
  id: string
  time: string
  type: string
  symbol: string
  qty: string
  status: string
}

type LoginRecordItem = {
  id: string
  time: string
  method: string
  device: string
  status: string
}

type AccountSummary = FundsSnapshot & {
  account?: string
  fundAccountId?: string
  securitiesAccountId?: string
  currency?: string
}

const state = reactive({
  accountId: 'admin',
  account: null as AccountSummary | null,
  funds: null as FundsSnapshot | null,
  holdings: [] as HoldingItem[],
  holdingsMeta: {
    asOf: '',
    totalMarketValue: 0,
  },
  orders: [] as OrderItem[],
  fills: [] as FillItem[],
  cashFlows: [] as CashFlowItem[],
  stockFlows: [] as StockFlowItem[],
  alerts: [] as AlertItem[],
  loginRecords: [] as LoginRecordItem[],
  loading: {
    account: false,
    funds: false,
    holdings: false,
    orders: false,
    fills: false,
    flows: false,
    alerts: false,
    loginRecords: false,
  },
  error: '' as string,
})

const setAccount = (accountId: string) => {
  state.accountId = accountId
}

const setError = (message: string) => {
  state.error = message
}

const resolveAccount = () => state.accountId || 'admin'

const refreshAccount = async () => {
  state.loading.account = true
  try {
    const data = await fetchAccount(resolveAccount())
    state.account = data
  } catch (error) {
    setError(error instanceof Error ? error.message : '账户信息加载失败')
  } finally {
    state.loading.account = false
  }
}

const refreshFunds = async () => {
  state.loading.funds = true
  try {
    const data = await fetchFunds(resolveAccount())
    state.funds = data
  } catch (error) {
    setError(error instanceof Error ? error.message : '资金信息加载失败')
  } finally {
    state.loading.funds = false
  }
}

const refreshHoldings = async () => {
  state.loading.holdings = true
  try {
    const data = await fetchHoldings(resolveAccount())
    state.holdings = data.holdings || []
    state.holdingsMeta = {
      asOf: data.asOf,
      totalMarketValue: data.totalMarketValue || 0,
    }
  } catch (error) {
    setError(error instanceof Error ? error.message : '持仓信息加载失败')
  } finally {
    state.loading.holdings = false
  }
}

const refreshOrders = async () => {
  state.loading.orders = true
  try {
    const data = await fetchOrders(resolveAccount())
    state.orders = data.orders || []
  } catch (error) {
    setError(error instanceof Error ? error.message : '委托加载失败')
  } finally {
    state.loading.orders = false
  }
}

const refreshFills = async () => {
  state.loading.fills = true
  try {
    const data = await fetchFills(resolveAccount())
    state.fills = data.fills || []
  } catch (error) {
    setError(error instanceof Error ? error.message : '成交回报加载失败')
  } finally {
    state.loading.fills = false
  }
}

const refreshFlows = async () => {
  state.loading.flows = true
  try {
    const [cash, stock] = await Promise.all([
      fetchCashFlows(resolveAccount()),
      fetchStockFlows(resolveAccount()),
    ])
    state.cashFlows = cash.cashFlows || []
    state.stockFlows = stock.stockFlows || []
  } catch (error) {
    setError(error instanceof Error ? error.message : '流水加载失败')
  } finally {
    state.loading.flows = false
  }
}

const refreshAlerts = async () => {
  state.loading.alerts = true
  try {
    const data = await fetchAlerts(resolveAccount())
    state.alerts = data.alerts || []
  } catch (error) {
    setError(error instanceof Error ? error.message : '提醒加载失败')
  } finally {
    state.loading.alerts = false
  }
}

const refreshLoginRecords = async () => {
  state.loading.loginRecords = true
  try {
    const data = await fetchLoginRecords(resolveAccount())
    state.loginRecords = data.records || []
  } catch (error) {
    setError(error instanceof Error ? error.message : '登录记录加载失败')
  } finally {
    state.loading.loginRecords = false
  }
}

const refreshAll = async () => {
  await Promise.all([
    refreshAccount(),
    refreshFunds(),
    refreshHoldings(),
    refreshOrders(),
    refreshFills(),
    refreshFlows(),
    refreshAlerts(),
    refreshLoginRecords(),
  ])
}

const placeOrder = async (payload: {
  symbol: string
  side: '买入' | '卖出'
  price: number
  quantity: number
  note?: string
}) => {
  const data = await apiPlaceOrder({
    account: resolveAccount(),
    ...payload,
  })

  await Promise.all([refreshFunds(), refreshHoldings(), refreshOrders(), refreshFills(), refreshFlows()])
  return data.order as OrderItem
}

const cancelOrder = async (orderId: string) => {
  const data = await apiCancelOrder(orderId)
  await Promise.all([refreshFunds(), refreshHoldings(), refreshOrders(), refreshFlows()])
  return data.order as OrderItem
}

const deposit = async (amount: number) => {
  await depositFunds({ account: resolveAccount(), amount })
  await Promise.all([refreshFunds(), refreshFlows(), refreshAccount()])
}

const withdraw = async (amount: number, password?: string) => {
  await withdrawFunds({ account: resolveAccount(), amount, password })
  await Promise.all([refreshFunds(), refreshFlows(), refreshAccount()])
}

const createAlert = async (payload: { symbol: string; condition: string; triggerPrice: string }) => {
  const data = await apiCreateAlert({ account: resolveAccount(), ...payload })
  await refreshAlerts()
  return data.alert as AlertItem
}

const updateAlert = async (alertId: string, payload: Record<string, unknown>) => {
  const data = await apiUpdateAlert(alertId, payload)
  await refreshAlerts()
  return data.alert as AlertItem
}

const deleteAlert = async (alertId: string) => {
  await apiDeleteAlert(alertId)
  await refreshAlerts()
}

const changeTradePasswordAction = async (payload: {
  currentPassword: string
  nextPassword: string
}) => {
  await changeTradePassword({ account: resolveAccount(), ...payload })
}

const changeWithdrawPasswordAction = async (payload: {
  currentPassword: string
  nextPassword: string
}) => {
  await changeWithdrawPassword({ account: resolveAccount(), ...payload })
}

const recordLogin = async (payload: { method: string; device: string; status?: string }) => {
  await addLoginRecord({
    account: resolveAccount(),
    time: new Date().toLocaleString('zh-CN', { hour12: false }),
    ...payload,
  })
  await refreshLoginRecords()
}

const availableFunds = computed(() => state.funds?.available ?? 0)

const holdingsMap = computed(() => {
  const map = new Map<string, HoldingItem>()
  state.holdings.forEach((item) => {
    map.set(item.symbol, item)
  })
  return map
})

const store = {
  state: readonly(state),
  setAccount,
  refreshAccount,
  refreshFunds,
  refreshHoldings,
  refreshOrders,
  refreshFills,
  refreshFlows,
  refreshAlerts,
  refreshLoginRecords,
  refreshAll,
  placeOrder,
  cancelOrder,
  deposit,
  withdraw,
  createAlert,
  updateAlert,
  deleteAlert,
  changeTradePassword: changeTradePasswordAction,
  changeWithdrawPassword: changeWithdrawPasswordAction,
  recordLogin,
  availableFunds,
  holdingsMap,
}

export type {
  OrderItem,
  OrderStatus,
  FillItem,
  AlertItem,
  AlertStatus,
  CashFlowItem,
  StockFlowItem,
  LoginRecordItem,
  HoldingItem,
  FundsSnapshot,
}

export const useTradingStore = () => {
  return store
}
