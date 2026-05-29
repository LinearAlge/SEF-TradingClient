const authAdapter = require('./adapters/authAdapter.cjs')
const db = require('./client-db.cjs')

const seedFromLegacy = (legacy) => {
  if (!legacy) return
  db.seedUser({
    account: legacy.account,
    password: legacy.password,
    name: legacy.name,
    firstLogin: legacy.firstLogin,
    publicKey: legacy.publicKey,
  })
}

module.exports = {
  seedFromLegacy,
  authAdapter,
}
