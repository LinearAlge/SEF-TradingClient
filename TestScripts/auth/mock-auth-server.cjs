const http = require('http')
const crypto = require('crypto')
const fs = require('fs')
const path = require('path')

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

const DB_PATH = path.join(__dirname, 'mock-auth-db.json')

const DEFAULT_RECORD = {
  account: 'admin',
  password: '123456',
  name: '测试用户',
  phone: '13800000000',
  idNumber: '110101199001012222',
  firstLogin: true,
  publicKey: null,
}

const loadAccountRecord = () => {
  if (!fs.existsSync(DB_PATH)) {
    return { ...DEFAULT_RECORD }
  }

  try {
    const raw = fs.readFileSync(DB_PATH, 'utf8')
    const parsed = JSON.parse(raw)
    return { ...DEFAULT_RECORD, ...parsed }
  } catch (error) {
    return { ...DEFAULT_RECORD }
  }
}

const saveAccountRecord = (record) => {
  fs.writeFileSync(DB_PATH, JSON.stringify(record, null, 2), 'utf8')
}

let accountRecord = loadAccountRecord()

const challenges = new Map()

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

const verifySignature = (challenge, signature, publicKey) => {
  try {
    const keyObject = crypto.createPublicKey({ key: publicKey, format: 'jwk' })
    return crypto.verify(
      'RSA-SHA256',
      Buffer.from(challenge, 'utf8'),
      keyObject,
      Buffer.from(signature, 'base64'),
    )
  } catch (error) {
    return false
  }
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
    parseJsonBody(req, res, (payload) => {
      const { account, password } = payload
      if (account !== accountRecord.account || password !== accountRecord.password) {
        sendJson(res, 401, { ok: false, message: '账号或密码错误' })
        return
      }

      if (!accountRecord.publicKey || accountRecord.firstLogin) {
        sendJson(res, 200, {
          ok: true,
          action: 'enroll',
          message: '首次登录需要绑定证书',
        })
        return
      }

      const challenge = crypto.randomBytes(32).toString('base64')
      challenges.set(account, challenge)
      sendJson(res, 200, {
        ok: true,
        action: 'verify',
        challenge,
      })
    })

    return
  }

  if (req.url === '/enroll' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const { account, publicKey } = payload
      if (account !== accountRecord.account) {
        sendJson(res, 401, { ok: false, message: '账户不存在' })
        return
      }

      if (!publicKey) {
        sendJson(res, 400, { ok: false, message: '缺少公钥' })
        return
      }

      accountRecord.publicKey = publicKey
      accountRecord.firstLogin = false
      saveAccountRecord(accountRecord)
      sendJson(res, 200, {
        ok: true,
        token: 'mock-token',
        user: {
          name: accountRecord.name,
          account: accountRecord.account,
        },
      })
    })

    return
  }

  if (req.url === '/verify' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const { account, signature } = payload
      if (account !== accountRecord.account) {
        sendJson(res, 401, { ok: false, message: '账户不存在' })
        return
      }

      const challenge = challenges.get(account)
      if (!challenge) {
        sendJson(res, 400, { ok: false, message: '挑战码已失效' })
        return
      }

      if (!accountRecord.publicKey || !signature) {
        sendJson(res, 400, { ok: false, message: '证书验证信息不完整' })
        return
      }

      const ok = verifySignature(challenge, signature, accountRecord.publicKey)
      challenges.delete(account)
      if (!ok) {
        sendJson(res, 401, { ok: false, message: '证书验证失败' })
        return
      }

      sendJson(res, 200, {
        ok: true,
        token: 'mock-token',
        user: {
          name: accountRecord.name,
          account: accountRecord.account,
        },
      })
    })

    return
  }

  if (req.url === '/rebind' && req.method === 'POST') {
    parseJsonBody(req, res, (payload) => {
      const { account, password, phone, idNumber } = payload

      if (account !== accountRecord.account || password !== accountRecord.password) {
        sendJson(res, 401, { ok: false, message: '账号或密码错误' })
        return
      }

      if (phone !== accountRecord.phone || idNumber !== accountRecord.idNumber) {
        sendJson(res, 403, { ok: false, message: '身份信息校验失败' })
        return
      }

      accountRecord.publicKey = null
      accountRecord.firstLogin = true
      saveAccountRecord(accountRecord)
      challenges.delete(account)
      sendJson(res, 200, {
        ok: true,
        message: '证书已重置，请重新登录绑定证书',
        user: {
          name: accountRecord.name,
          account: accountRecord.account,
        },
      })
    })

    return
  }

  sendJson(res, 404, { ok: false, message: 'Not found' })
})

server.listen(PORT, () => {
  console.log(`Mock auth server running at http://localhost:${PORT}`)
})
