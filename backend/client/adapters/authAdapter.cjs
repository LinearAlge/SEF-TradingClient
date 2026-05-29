const crypto = require('crypto')
const db = require('../client-db.cjs')

const challenges = new Map()

const login = (account) => {
  const user = db.getUser(account)
  if (!user) {
    return { ok: false, status: 403, message: '未开通客户端权限，请先申请', action: 'apply' }
  }

  const cert = db.getCertificate(account)
  if (!cert || user.first_login) {
    return { ok: true, action: 'enroll', message: '首次登录需要绑定证书' }
  }

  const challenge = crypto.randomBytes(32).toString('base64')
  challenges.set(account, challenge)
  return { ok: true, action: 'verify', challenge }
}

const enroll = (account, publicKey) => {
  const user = db.getUser(account)
  if (!user) {
    return { ok: false, status: 401, message: '账户不存在' }
  }
  if (!publicKey) {
    return { ok: false, status: 400, message: '缺少公钥' }
  }

  db.upsertCertificate(account, publicKey)
  db.updateFirstLogin(account, false)

  return {
    ok: true,
    token: 'mock-token',
    user: {
      name: user.name,
      account: user.account,
    },
  }
}

const verify = (account, signature) => {
  const user = db.getUser(account)
  if (!user) {
    return { ok: false, status: 401, message: '账户不存在' }
  }

  const challenge = challenges.get(account)
  if (!challenge) {
    return { ok: false, status: 400, message: '挑战码已失效' }
  }

  const cert = db.getCertificate(account)
  if (!cert || !signature) {
    return { ok: false, status: 400, message: '证书验证信息不完整' }
  }

  const publicKey = JSON.parse(cert.public_key)
  let ok = false
  try {
    const keyObject = crypto.createPublicKey({ key: publicKey, format: 'jwk' })
    ok = crypto.verify(
      'RSA-SHA256',
      Buffer.from(challenge, 'utf8'),
      keyObject,
      Buffer.from(signature, 'base64'),
    )
  } catch (error) {
    ok = false
  }

  challenges.delete(account)
  if (!ok) {
    return { ok: false, status: 401, message: '证书验证失败' }
  }

  return {
    ok: true,
    token: 'mock-token',
    user: {
      name: user.name,
      account: user.account,
    },
  }
}

const rebind = (account, password) => {
  const user = db.getUser(account)
  if (!user || user.password !== password) {
    return { ok: false, status: 401, message: '账号或密码错误' }
  }

  db.clearCertificate(account)
  db.updateFirstLogin(account, true)

  return {
    ok: true,
    message: '证书已重置，请重新登录绑定证书',
    user: {
      name: user.name,
      account: user.account,
    },
  }
}

const getProfile = (account) => {
  const user = db.getUser(account)
  if (!user) {
    return { ok: false, status: 404, message: '账户不存在' }
  }

  return {
    ok: true,
    user: {
      account: user.account,
      name: user.name,
    },
  }
}

module.exports = {
  login,
  enroll,
  verify,
  rebind,
  getProfile,
}
