const fetchJson = async (url, options) => {
  const response = await fetch(url, options)
  const data = await response.json().catch(() => ({}))
  if (!response.ok || !data.ok) {
    const message = data.message || '资金服务请求失败'
    throw new Error(message)
  }
  return data
}

const resolveBase = () =>
  process.env.FUNDS_SERVICE_BASE_URL || 'http://localhost:3021'

const getAccountProfile = async (account) =>
  fetchJson(`${resolveBase()}/accounts?account=${encodeURIComponent(account)}`)

const getFunds = async (account) =>
  fetchJson(`${resolveBase()}/funds?account=${encodeURIComponent(account)}`)

const deposit = async (payload) =>
  fetchJson(`${resolveBase()}/funds/deposit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

const withdraw = async (payload) =>
  fetchJson(`${resolveBase()}/funds/withdraw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

const getCashFlows = async (account) =>
  fetchJson(`${resolveBase()}/cash-flows?account=${encodeURIComponent(account)}`)

const changeTradePassword = async (payload) =>
  fetchJson(`${resolveBase()}/passwords/trade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

const applyTradeFill = async (payload) =>
  fetchJson(`${resolveBase()}/funds/apply-fill`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

const verifyTradePassword = async (payload) =>
  fetchJson(`${resolveBase()}/passwords/trade/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

const changeWithdrawPassword = async (payload) =>
  fetchJson(`${resolveBase()}/passwords/withdraw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

module.exports = {
  getAccountProfile,
  getFunds,
  deposit,
  withdraw,
  getCashFlows,
  changeTradePassword,
  applyTradeFill,
  verifyTradePassword,
  changeWithdrawPassword,
}
