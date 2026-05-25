const http = require('http')

const PORT = process.env.PORT || 3001

const sendJson = (res, statusCode, payload) => {
  const body = JSON.stringify(payload)
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
  })
  res.end(body)
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    })
    res.end()
    return
  }

  if (req.url === '/health' && req.method === 'GET') {
    sendJson(res, 200, { ok: true })
    return
  }

  if (req.url === '/login' && req.method === 'POST') {
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

      const { account, password } = payload
      if (account === 'admin' && password === '123456') {
        sendJson(res, 200, {
          ok: true,
          token: 'mock-token',
          user: {
            name: '测试用户',
            account,
          },
        })
        return
      }

      sendJson(res, 401, { ok: false, message: '账号或密码错误' })
    })

    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Mock auth server running at http://localhost:${PORT}`)
})
