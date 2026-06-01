type SessionPayload = {
  token?: string
  investorId?: string
  fundAccountId?: string
  securityAccountId?: string
  expiresAt?: string
}

let unauthorizedPrompted = false

export const getSessionToken = () => localStorage.getItem('trading-token')

export const getSessionExpiry = () => localStorage.getItem('trading-token-expires-at')

export const isSessionExpired = () => {
  const expiresAt = getSessionExpiry()
  if (!expiresAt) return false
  const expiresTime = new Date(expiresAt).getTime()
  if (Number.isNaN(expiresTime)) return false
  return Date.now() > expiresTime
}

export const saveSession = (payload: SessionPayload) => {
  if (payload.token) localStorage.setItem('trading-token', payload.token)
  if (payload.investorId) localStorage.setItem('trading-investor-id', payload.investorId)
  if (payload.fundAccountId) localStorage.setItem('trading-fund-account-id', payload.fundAccountId)
  if (payload.securityAccountId)
    localStorage.setItem('trading-security-account-id', payload.securityAccountId)
  if (payload.expiresAt) localStorage.setItem('trading-token-expires-at', payload.expiresAt)
}

export const clearSession = () => {
  localStorage.removeItem('trading-token')
  localStorage.removeItem('trading-investor-id')
  localStorage.removeItem('trading-fund-account-id')
  localStorage.removeItem('trading-security-account-id')
  localStorage.removeItem('trading-token-expires-at')
}

export const handleUnauthorized = (message = '登录已过期，请重新登录。') => {
  if (unauthorizedPrompted) return
  unauthorizedPrompted = true
  clearSession()
  window.alert(message)
  window.location.assign('/login')
}