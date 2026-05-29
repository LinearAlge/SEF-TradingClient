const path = require('path')
const fs = require('fs')
const Database = require('better-sqlite3')

const DB_PATH = path.join(__dirname, 'client.sqlite')

const ensureDir = (filePath) => {
  const dir = path.dirname(filePath)
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }
}

const initDatabase = () => {
  ensureDir(DB_PATH)
  const db = new Database(DB_PATH)
  db.pragma('journal_mode = WAL')

  db.exec(`
    CREATE TABLE IF NOT EXISTS client_users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      name TEXT,
      phone TEXT,
      id_number TEXT,
      first_login INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS client_certificates (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account TEXT NOT NULL,
      public_key TEXT,
      updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS client_sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account TEXT NOT NULL,
      token TEXT NOT NULL,
      created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS client_login_records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account TEXT NOT NULL,
      time TEXT,
      method TEXT,
      device TEXT,
      status TEXT
    );

    CREATE TABLE IF NOT EXISTS client_applications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account TEXT NOT NULL,
      type TEXT,
      status TEXT,
      created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS client_alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account TEXT NOT NULL,
      symbol TEXT NOT NULL,
      condition TEXT NOT NULL,
      trigger_price TEXT NOT NULL,
      current_price TEXT,
      status TEXT,
      last_triggered TEXT,
      created_at TEXT,
      updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS client_notifications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account TEXT NOT NULL,
      title TEXT,
      content TEXT,
      read INTEGER DEFAULT 0,
      created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS client_preferences (
      account TEXT PRIMARY KEY,
      data TEXT
    );

    CREATE TABLE IF NOT EXISTS client_watchlist (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account TEXT NOT NULL,
      symbol TEXT NOT NULL
    );
  `)

  return db
}

const db = initDatabase()

const seedUser = ({ account, password, name, firstLogin, publicKey }) => {
  const exists = db
    .prepare('SELECT 1 FROM client_users WHERE account = ?')
    .get(account)
  if (!exists) {
    db.prepare(
      'INSERT INTO client_users (account, password, name, first_login) VALUES (?, ?, ?, ?)',
    ).run(account, password, name, firstLogin ? 1 : 0)
  }

  const certExists = db
    .prepare('SELECT 1 FROM client_certificates WHERE account = ?')
    .get(account)
  if (!certExists && publicKey) {
    db.prepare(
      'INSERT INTO client_certificates (account, public_key, updated_at) VALUES (?, ?, ?)',
    ).run(account, JSON.stringify(publicKey), new Date().toISOString())
  }
}

const createApplication = ({ account, type, status, createdAt }) => {
  db.prepare(
    'INSERT INTO client_applications (account, type, status, created_at) VALUES (?, ?, ?, ?)',
  ).run(account, type, status, createdAt)
}

const listApplications = (account) =>
  db.prepare('SELECT * FROM client_applications WHERE account = ? ORDER BY id DESC').all(account)

const getUser = (account) =>
  db.prepare('SELECT * FROM client_users WHERE account = ?').get(account)

const updateUserPassword = (account, nextPassword) =>
  db.prepare('UPDATE client_users SET password = ? WHERE account = ?').run(nextPassword, account)

const updateFirstLogin = (account, firstLogin) =>
  db.prepare('UPDATE client_users SET first_login = ? WHERE account = ?').run(firstLogin ? 1 : 0, account)

const getCertificate = (account) =>
  db.prepare('SELECT * FROM client_certificates WHERE account = ?').get(account)

const upsertCertificate = (account, publicKey) => {
  const existing = getCertificate(account)
  const payload = JSON.stringify(publicKey)
  if (existing) {
    db.prepare('UPDATE client_certificates SET public_key = ?, updated_at = ? WHERE account = ?')
      .run(payload, new Date().toISOString(), account)
  } else {
    db.prepare('INSERT INTO client_certificates (account, public_key, updated_at) VALUES (?, ?, ?)')
      .run(account, payload, new Date().toISOString())
  }
}

const clearCertificate = (account) => {
  db.prepare('DELETE FROM client_certificates WHERE account = ?').run(account)
}

const addLoginRecord = (record) => {
  db.prepare(
    'INSERT INTO client_login_records (account, time, method, device, status) VALUES (?, ?, ?, ?, ?)',
  ).run(record.account, record.time, record.method, record.device, record.status)
}

const listLoginRecords = (account) =>
  db.prepare('SELECT * FROM client_login_records WHERE account = ? ORDER BY id DESC').all(account)

const listAlerts = (account) =>
  db.prepare('SELECT * FROM client_alerts WHERE account = ? ORDER BY id DESC').all(account)

const createAlert = (alert) => {
  const result = db.prepare(
    'INSERT INTO client_alerts (account, symbol, condition, trigger_price, current_price, status, last_triggered, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
  ).run(
    alert.account,
    alert.symbol,
    alert.condition,
    alert.trigger_price,
    alert.current_price || '--',
    alert.status || '监控中',
    alert.last_triggered || '--',
    alert.created_at,
    alert.updated_at,
  )
  return result.lastInsertRowid
}

const updateAlert = (id, patch) => {
  const columns = Object.keys(patch)
  if (columns.length === 0) return
  const assignments = columns.map((col) => `${col} = ?`).join(', ')
  const values = columns.map((col) => patch[col])
  db.prepare(`UPDATE client_alerts SET ${assignments} WHERE id = ?`).run(...values, id)
}

const deleteAlert = (id) => {
  db.prepare('DELETE FROM client_alerts WHERE id = ?').run(id)
}

const listNotifications = (account) =>
  db.prepare('SELECT * FROM client_notifications WHERE account = ? ORDER BY id DESC').all(account)

const markNotificationRead = (id) =>
  db.prepare('UPDATE client_notifications SET read = 1 WHERE id = ?').run(id)

const getPreferences = (account) =>
  db.prepare('SELECT data FROM client_preferences WHERE account = ?').get(account)

const updatePreferences = (account, data) => {
  const exists = getPreferences(account)
  if (exists) {
    db.prepare('UPDATE client_preferences SET data = ? WHERE account = ?').run(data, account)
  } else {
    db.prepare('INSERT INTO client_preferences (account, data) VALUES (?, ?)').run(account, data)
  }
}

const listWatchlist = (account) =>
  db.prepare('SELECT symbol FROM client_watchlist WHERE account = ? ORDER BY id DESC').all(account)

const toggleWatchlist = (account, symbol) => {
  const existing = db
    .prepare('SELECT id FROM client_watchlist WHERE account = ? AND symbol = ?')
    .get(account, symbol)
  if (existing) {
    db.prepare('DELETE FROM client_watchlist WHERE id = ?').run(existing.id)
    return false
  }
  db.prepare('INSERT INTO client_watchlist (account, symbol) VALUES (?, ?)').run(account, symbol)
  return true
}

module.exports = {
  seedUser,
  getUser,
  createApplication,
  listApplications,
  updateUserPassword,
  updateFirstLogin,
  getCertificate,
  upsertCertificate,
  clearCertificate,
  addLoginRecord,
  listLoginRecords,
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
