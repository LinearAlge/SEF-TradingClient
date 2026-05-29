const http = require('http')
const path = require('path')
const fs = require('fs')

const authService = require('./client-auth-service.cjs')
const clientState = require('./client-state-service.cjs')
const authAdapter = require('./adapters/authAdapter.cjs')
const clientDb = require('./client-db.cjs')
const fundsAdapter = require('./adapters/fundsAdapter.cjs')
const securitiesAdapter = require('./adapters/securitiesAdapter.cjs')
const exchangeAdapter = require('./adapters/exchangeAdapter.cjs')
const marketAdapter = require('./adapters/marketAdapter.cjs')

const PORT = process.env.CLIENT_API_PORT || 3010

// Legacy TestScripts seeding removed; client accounts must apply before use.

const sendJson = (res, statusCode, payload) => {
  const body = JSON.stringify(payload)
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
  })
  res.end(body)
}

const parseJsonBody = (req, res, callback) => {
  let rawBody = ''
  req.on('data', (chunk) => {
    rawBody += chunk
    if (rawBody.length > 1e6) {
      req.destroy()
    }
  })

  req.on('end', () => {
    let payload = {}
    try {
      payload = rawBody ? JSON.parse(rawBody) : {}
    } catch (error) {
      sendJson(res, 400, { ok: false, message: '无效的 JSON 数据' })
      return
    }

    callback(payload)
  })
}

const resolveAccount = (reqUrl) => {
  const url = new URL(reqUrl, 'http://localhost')
  return url.searchParams.get('account') || 'admin'
}

const mergeFundsWithHoldings = (funds, holdings) => {
  const available = Number(funds?.available ?? 0)
  const frozen = Number(funds?.frozen ?? 0)
  const marketValue = Number(holdings?.totalMarketValue ?? funds?.marketValue ?? 0)
  return {
    ...funds,
    marketValue,
    totalEquity: Number((available + frozen + marketValue).toFixed(2)),
  }
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
    })
    res.end()
    return
  }

  if (req.url === '/health' && req.method === 'GET') {
    sendJson(res, 200, { ok: true })
    return
  }

  if (req.url === '/api/auth/login' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = (payload.account || '').trim()
      const password = payload.password
      if (!account || !password) {
        sendJson(res, 400, { ok: false, message: '账户与密码不能为空' })
        return
      }

      const user = clientDb.getUser(account)
      if (!user) {
        sendJson(res, 403, { ok: false, message: '未开通客户端权限，请先申请', action: 'apply' })
        return
      }

      fundsAdapter
        .verifyTradePassword({ account, password })
        .then(() => {
          const result = authAdapter.login(account)
          if (!result.ok) {
            sendJson(res, result.status, result)
            return
          }
          sendJson(res, 200, result)
        })
        .catch((error) => {
          const message = error.message || '账号或密码错误'
          const status = message === '交易密码错误' ? 401 : 400
          sendJson(res, status, { ok: false, message })
        })
    })
    return
  }

  if (req.url === '/api/auth/enroll' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const result = authAdapter.enroll(payload.account, payload.publicKey)
      if (!result.ok) {
        sendJson(res, result.status, result)
        return
      }
      sendJson(res, 200, result)
    })
    return
  }

  if (req.url === '/api/auth/verify' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const result = authAdapter.verify(payload.account, payload.signature)
      if (!result.ok) {
        sendJson(res, result.status, result)
        return
      }
      sendJson(res, 200, result)
    })
    return
  }

  if (req.url === '/api/auth/rebind' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = (payload.account || '').trim()
      const password = payload.password
      const phone = (payload.phone || '').trim()
      const idNumber = (payload.idNumber || '').trim()
      if (!account || !password) {
        sendJson(res, 400, { ok: false, message: '账户与密码不能为空' })
        return
      }
      if (!phone || !idNumber) {
        sendJson(res, 400, { ok: false, message: '手机号与身份证号不能为空' })
        return
      }

      fundsAdapter
        .getAccountProfile(account)
        .then((profile) => {
          if (profile.phone !== phone || profile.idNumber !== idNumber) {
            sendJson(res, 403, { ok: false, message: '身份信息校验失败' })
            return
          }

          const result = authAdapter.rebind(account, password)
          if (!result.ok) {
            sendJson(res, result.status, result)
            return
          }
          sendJson(res, 200, result)
        })
        .catch((error) => {
          sendJson(res, 400, { ok: false, message: error.message || '资金账户不存在' })
        })
    })
    return
  }

  if (req.url.startsWith('/api/auth/me') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    const result = authAdapter.getProfile(account)
    if (!result.ok) {
      sendJson(res, result.status, result)
      return
    }
    sendJson(res, 200, result)
    return
  }

  if (req.url.startsWith('/api/account/summary') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    fundsAdapter
      .getFunds(account)
      .then((funds) =>
        securitiesAdapter
          .getHoldings(account)
          .then((holdings) => sendJson(res, 200, mergeFundsWithHoldings(funds, holdings)))
          .catch(() => sendJson(res, 200, mergeFundsWithHoldings(funds))),
      )
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url.startsWith('/api/account/funds') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    fundsAdapter
      .getFunds(account)
      .then((funds) =>
        securitiesAdapter
          .getHoldings(account)
          .then((holdings) => sendJson(res, 200, mergeFundsWithHoldings(funds, holdings)))
          .catch(() => sendJson(res, 200, mergeFundsWithHoldings(funds))),
      )
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url === '/api/account/funds/deposit' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      fundsAdapter
        .deposit(payload)
        .then((data) => sendJson(res, 200, data))
        .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    })
    return
  }

  if (req.url === '/api/account/funds/withdraw' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      fundsAdapter
        .withdraw(payload)
        .then((data) => sendJson(res, 200, data))
        .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    })
    return
  }

  if (req.url === '/api/account/passwords/trade' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      fundsAdapter
        .changeTradePassword(payload)
        .then((data) => sendJson(res, 200, data))
        .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    })
    return
  }

  if (req.url === '/api/account/passwords/withdraw' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      fundsAdapter
        .changeWithdrawPassword(payload)
        .then((data) => sendJson(res, 200, data))
        .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    })
    return
  }

  if (req.url.startsWith('/api/account/holdings') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    securitiesAdapter
      .getHoldings(account)
      .then((data) => sendJson(res, 200, data))
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url.startsWith('/api/account/cash-flows') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    fundsAdapter
      .getCashFlows(account)
      .then((data) => sendJson(res, 200, data))
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url.startsWith('/api/account/stock-flows') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    securitiesAdapter
      .getStockFlows(account)
      .then((data) => sendJson(res, 200, data))
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url.startsWith('/api/market/stocks') && req.method === 'GET') {
    const url = new URL(req.url, 'http://localhost')
    const symbol = url.searchParams.get('symbol')
    const query = url.searchParams.get('query') || ''
    const board = url.searchParams.get('board') || ''

    const handler = symbol ? marketAdapter.getStock(symbol) : marketAdapter.getStocks(query, board)
    handler
      .then((data) => sendJson(res, 200, data))
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url.startsWith('/api/market/quotes') && req.method === 'GET') {
    const url = new URL(req.url, 'http://localhost')
    const symbols = url.searchParams.get('symbols')
    const list = symbols ? symbols.split(',').filter(Boolean) : []
    marketAdapter
      .getQuotes(list)
      .then((data) => sendJson(res, 200, data))
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url.startsWith('/api/trade/orders') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    exchangeAdapter
      .getOrders(account)
      .then((data) => sendJson(res, 200, data))
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url === '/api/trade/orders' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      exchangeAdapter
        .placeOrder(payload)
        .then((data) => {
          const account = payload.account || 'admin'
          const fills = Array.isArray(data.fills) ? data.fills : []
          if (fills.length === 0) {
            sendJson(res, 200, data)
            return
          }

          Promise.all(
            fills.map((fill) =>
              Promise.all([
                fundsAdapter.applyTradeFill({ account, ...fill }),
                securitiesAdapter.applyTradeFill({ account, ...fill }),
              ]),
            ),
          )
            .then(() => sendJson(res, 200, data))
            .catch((error) => {
              sendJson(res, 500, { ok: false, message: error.message || '清算更新失败' })
            })
        })
        .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    })
    return
  }

  if (req.url.startsWith('/api/trade/orders/') && req.method === 'POST') {
    const match = req.url.match(/\/api\/trade\/orders\/(.+)\/cancel/)
    if (!match) {
      sendJson(res, 404, { ok: false, message: 'Not found' })
      return
    }
    const orderId = match[1]
    exchangeAdapter
      .cancelOrder(orderId)
      .then((data) => sendJson(res, 200, data))
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

    if (req.url === '/api/client/applications' && req.method === 'POST') {
      parseJsonBody(req, res, (payload) => {
        const account = (payload.account || '').trim()
        const password = payload.password
        const phone = (payload.phone || '').trim()
        if (!account || !password) {
          sendJson(res, 400, { ok: false, message: '账户与密码不能为空' })
          return
        }
        if (!phone) {
          sendJson(res, 400, { ok: false, message: '手机号不能为空' })
          return
        }

        if (clientDb.getUser(account)) {
          sendJson(res, 400, { ok: false, message: '账户已开通客户端权限' })
          return
        }

        Promise.all([fundsAdapter.getFunds(account), fundsAdapter.getAccountProfile(account)])
          .then(([, profile]) => {
            if (profile.phone !== phone) {
              sendJson(res, 403, { ok: false, message: '手机号校验失败' })
              return
            }

            const now = new Date().toISOString()
            clientDb.createApplication({
              account,
              type: 'client-access',
              status: 'approved',
              createdAt: now,
            })
            authService.seedFromLegacy({
              account,
              password,
              name: payload.name || '新用户',
              firstLogin: true,
              publicKey: null,
            })
            sendJson(res, 200, { ok: true, status: 'approved' })
          })
          .catch((error) => {
            sendJson(res, 400, { ok: false, message: error.message || '资金账户不存在' })
          })
      })
      return
    }

    if (req.url.startsWith('/api/client/applications') && req.method === 'GET') {
      const account = resolveAccount(req.url)
      const list = clientDb.listApplications(account)
      sendJson(res, 200, { ok: true, applications: list })
      return
    }

  if (req.url.startsWith('/api/trade/fills') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    exchangeAdapter
      .getFills(account)
      .then((data) => sendJson(res, 200, data))
      .catch((error) => sendJson(res, 500, { ok: false, message: error.message }))
    return
  }

  if (req.url.startsWith('/api/client/alerts') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    const alerts = clientState.listAlerts(account)
    sendJson(res, 200, { ok: true, alerts })
    return
  }

  if (req.url.startsWith('/api/client/login-records') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    const records = clientDb.listLoginRecords(account)
    sendJson(res, 200, { ok: true, records })
    return
  }

  if (req.url === '/api/client/login-records' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      clientDb.addLoginRecord({
        account,
        time: payload.time || new Date().toLocaleString('zh-CN', { hour12: false }),
        method: payload.method || '密码登录',
        device: payload.device || '未知',
        status: payload.status || '成功',
      })
      sendJson(res, 200, { ok: true })
    })
    return
  }

  if (req.url === '/api/client/alerts' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const alert = clientState.createAlert(account, payload)
      sendJson(res, 200, { ok: true, alert })
    })
    return
  }

  if (req.url.startsWith('/api/client/alerts/') && req.method === 'PATCH') {
    const match = req.url.match(/\/api\/client\/alerts\/(.+)/)
    if (!match) {
      sendJson(res, 404, { ok: false, message: 'Not found' })
      return
    }
    const alertId = match[1]
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      const alert = clientState.updateAlert(account, alertId, payload)
      sendJson(res, 200, { ok: true, alert })
    })
    return
  }

  if (req.url.startsWith('/api/client/alerts/') && req.method === 'DELETE') {
    const match = req.url.match(/\/api\/client\/alerts\/(.+)/)
    if (!match) {
      sendJson(res, 404, { ok: false, message: 'Not found' })
      return
    }
    const alertId = match[1]
    clientState.deleteAlert(alertId)
    sendJson(res, 200, { ok: true })
    return
  }

  if (req.url.startsWith('/api/client/notifications') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    const notifications = clientState.listNotifications(account)
    sendJson(res, 200, { ok: true, notifications })
    return
  }

  if (req.url.startsWith('/api/client/notifications/') && req.method === 'PATCH') {
    const match = req.url.match(/\/api\/client\/notifications\/(.+)\/read/)
    if (!match) {
      sendJson(res, 404, { ok: false, message: 'Not found' })
      return
    }
    clientState.markNotificationRead(match[1])
    sendJson(res, 200, { ok: true })
    return
  }

  if (req.url.startsWith('/api/client/watchlist') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    const watchlist = clientState.listWatchlist(account).map((item) => item.symbol)
    sendJson(res, 200, { ok: true, watchlist })
    return
  }

  if (req.url.startsWith('/api/client/watchlist/') && req.method === 'POST') {
    const match = req.url.match(/\/api\/client\/watchlist\/(.+)\/toggle/)
    if (!match) {
      sendJson(res, 404, { ok: false, message: 'Not found' })
      return
    }
    const symbol = match[1]
    const account = resolveAccount(req.url)
    const enabled = clientState.toggleWatchlist(account, symbol)
    sendJson(res, 200, { ok: true, enabled })
    return
  }

  if (req.url.startsWith('/api/client/preferences') && req.method === 'GET') {
    const account = resolveAccount(req.url)
    const preferences = clientState.getPreferences(account)
    sendJson(res, 200, { ok: true, preferences: preferences?.data ? JSON.parse(preferences.data) : {} })
    return
  }

  if (req.url.startsWith('/api/client/preferences') && req.method === 'PATCH') {
    parseJsonBody(req, res, (payload) => {
      const account = payload.account || 'admin'
      clientState.updatePreferences(account, JSON.stringify(payload))
      sendJson(res, 200, { ok: true })
    })
    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Client gateway server running at http://localhost:${PORT}`)
})
