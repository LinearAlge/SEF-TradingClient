const db = require('./client-db.cjs')

const normalizeAlert = (alert) => {
  if (!alert) return alert
  return {
    id: alert.id,
    symbol: alert.symbol,
    condition: alert.condition,
    triggerPrice: alert.trigger_price,
    currentPrice: alert.current_price,
    status: alert.status,
    lastTriggered: alert.last_triggered,
    createdAt: alert.created_at,
    updatedAt: alert.updated_at,
  }
}

const listAlerts = (account) => db.listAlerts(account).map(normalizeAlert)

const createAlert = (account, payload) => {
  const now = new Date().toISOString()
  const id = db.createAlert({
    account,
    symbol: payload.symbol,
    condition: payload.condition || '高于',
    trigger_price: payload.triggerPrice,
    current_price: payload.currentPrice || '--',
    status: payload.status || '监控中',
    last_triggered: payload.lastTriggered || '--',
    created_at: now,
    updated_at: now,
  })
  const alert = db.listAlerts(account).find((item) => item.id === id)
  return normalizeAlert(alert)
}

const normalizeAlertPatch = (patch) => {
  const allowed = new Set([
    'symbol',
    'condition',
    'trigger_price',
    'current_price',
    'status',
    'last_triggered',
  ])
  const mapped = {}
  Object.entries(patch || {}).forEach(([key, value]) => {
    let normalized = key
    if (key === 'triggerPrice') normalized = 'trigger_price'
    if (key === 'currentPrice') normalized = 'current_price'
    if (key === 'lastTriggered') normalized = 'last_triggered'
    if (allowed.has(normalized)) {
      mapped[normalized] = value
    }
  })
  return mapped
}

const updateAlert = (account, alertId, patch) => {
  db.updateAlert(alertId, {
    ...normalizeAlertPatch(patch),
    updated_at: new Date().toISOString(),
  })
  const alert = db.listAlerts(account).find((item) => item.id === Number(alertId))
  return normalizeAlert(alert)
}

const deleteAlert = (alertId) => {
  db.deleteAlert(alertId)
}

const listNotifications = (account) => db.listNotifications(account)

const markNotificationRead = (notificationId) => db.markNotificationRead(notificationId)

const getPreferences = (account) => db.getPreferences(account)

const updatePreferences = (account, data) => db.updatePreferences(account, data)

const listWatchlist = (account) => db.listWatchlist(account)

const toggleWatchlist = (account, symbol) => db.toggleWatchlist(account, symbol)

module.exports = {
  listAlerts,
  createAlert,
  updateAlert,
  deleteAlert,
  listNotifications,
  markNotificationRead,
  getPreferences,
  updatePreferences,
  listWatchlist,
  toggleWatchlist,
}
