type OrderStatus = '未成交' | '部分成交' | '已成交' | '已撤单' | '已过期' | '已拒绝'

type AlertStatus = '监控中' | '已暂停' | '已触发'

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

type StoreKey =
  | 'trading-orders'
  | 'trading-fills'
  | 'trading-alerts'
  | 'trading-cash-flows'
  | 'trading-stock-flows'
  | 'trading-login-records'
  | 'trading-watchlist'

const readStore = <T>(key: StoreKey, fallback: T): T => {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return fallback
    return JSON.parse(raw) as T
  } catch (error) {
    return fallback
  }
}

const writeStore = <T>(key: StoreKey, value: T) => {
  localStorage.setItem(key, JSON.stringify(value))
}

export const loadOrders = () => readStore<OrderItem[]>('trading-orders', [])

export const saveOrders = (items: OrderItem[]) => writeStore('trading-orders', items)

export const addOrder = (order: OrderItem) => {
  const items = loadOrders()
  const next = [order, ...items]
  saveOrders(next)
  return next
}

export const updateOrderStatus = (id: string, status: OrderStatus) => {
  const items = loadOrders().map((item) => (item.id === id ? { ...item, status } : item))
  saveOrders(items)
  return items
}

export const loadFills = () => readStore<FillItem[]>('trading-fills', [])

export const addFill = (fill: FillItem) => {
  const items = loadFills()
  const next = [fill, ...items]
  writeStore('trading-fills', next)
  return next
}

export const loadAlerts = () => readStore<AlertItem[]>('trading-alerts', [])

export const saveAlerts = (items: AlertItem[]) => writeStore('trading-alerts', items)

export const addAlert = (alert: AlertItem) => {
  const items = loadAlerts()
  const next = [alert, ...items]
  saveAlerts(next)
  return next
}

export const loadCashFlows = () => readStore<CashFlowItem[]>('trading-cash-flows', [])

export const addCashFlow = (flow: CashFlowItem) => {
  const items = loadCashFlows()
  const next = [flow, ...items]
  writeStore('trading-cash-flows', next)
  return next
}

export const loadStockFlows = () => readStore<StockFlowItem[]>('trading-stock-flows', [])

export const addStockFlow = (flow: StockFlowItem) => {
  const items = loadStockFlows()
  const next = [flow, ...items]
  writeStore('trading-stock-flows', next)
  return next
}

export const loadLoginRecords = () => readStore<LoginRecordItem[]>('trading-login-records', [])

export const addLoginRecord = (record: LoginRecordItem) => {
  const items = loadLoginRecords()
  const next = [record, ...items]
  writeStore('trading-login-records', next)
  return next
}

export const loadWatchlist = () => readStore<string[]>('trading-watchlist', [])

export const saveWatchlist = (items: string[]) => writeStore('trading-watchlist', items)

export const toggleWatchlist = (symbol: string) => {
  const items = loadWatchlist()
  const exists = items.includes(symbol)
  const next = exists ? items.filter((item) => item !== symbol) : [symbol, ...items]
  saveWatchlist(next)
  return next
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
}
