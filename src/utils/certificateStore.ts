const DB_NAME = 'trading-client'
const STORE_NAME = 'certificates'
const KEY_ID = 'device-keypair'

const openDatabase = (): Promise<IDBDatabase> =>
  new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1)

    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME)
      }
    }

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })

const withStore = async <T>(mode: IDBTransactionMode, handler: (store: IDBObjectStore) => void) => {
  const db = await openDatabase()
  return new Promise<T>((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, mode)
    const store = transaction.objectStore(STORE_NAME)
    handler(store)

    transaction.oncomplete = () => resolve(undefined as T)
    transaction.onerror = () => reject(transaction.error)
  })
}

const getValue = async <T>(key: string): Promise<T | null> => {
  const db = await openDatabase()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, 'readonly')
    const store = transaction.objectStore(STORE_NAME)
    const request = store.get(key)

    request.onsuccess = () => resolve((request.result as T) ?? null)
    request.onerror = () => reject(request.error)
  })
}

const setValue = async <T>(key: string, value: T) =>
  withStore('readwrite', (store) => {
    store.put(value, key)
  })

const deleteValue = async (key: string) =>
  withStore('readwrite', (store) => {
    store.delete(key)
  })

const keyAlgorithm: RsaHashedKeyGenParams = {
  name: 'RSASSA-PKCS1-v1_5',
  modulusLength: 2048,
  publicExponent: new Uint8Array([1, 0, 1]),
  hash: 'SHA-256',
}

const importAlgorithm: RsaHashedImportParams = {
  name: 'RSASSA-PKCS1-v1_5',
  hash: 'SHA-256',
}

const exportKeyPair = async (keyPair: CryptoKeyPair) => {
  const publicJwk = await crypto.subtle.exportKey('jwk', keyPair.publicKey)
  const privateJwk = await crypto.subtle.exportKey('jwk', keyPair.privateKey)

  return { publicJwk, privateJwk }
}

export const createAndStoreKeyPair = async () => {
  const keyPair = await crypto.subtle.generateKey(keyAlgorithm, true, ['sign', 'verify'])
  const { publicJwk, privateJwk } = await exportKeyPair(keyPair)

  await setValue(KEY_ID, {
    publicJwk,
    privateJwk,
    createdAt: Date.now(),
  })

  return { keyPair, publicJwk }
}

export const loadStoredKeyPair = async () => {
  const record = await getValue<{
    publicJwk: JsonWebKey
    privateJwk: JsonWebKey
    createdAt: number
  }>(KEY_ID)

  if (!record) {
    return null
  }

  const publicKey = await crypto.subtle.importKey(
    'jwk',
    record.publicJwk,
    importAlgorithm,
    true,
    ['verify'],
  )

  const privateKey = await crypto.subtle.importKey(
    'jwk',
    record.privateJwk,
    importAlgorithm,
    true,
    ['sign'],
  )

  return {
    publicKey,
    privateKey,
    publicJwk: record.publicJwk,
    createdAt: record.createdAt,
  }
}

export const ensureStoredKeyPair = async () => {
  const existing = await loadStoredKeyPair()
  if (existing) {
    return { keyPair: { publicKey: existing.publicKey, privateKey: existing.privateKey }, publicJwk: existing.publicJwk }
  }

  return createAndStoreKeyPair()
}

export const clearStoredKeyPair = async () => {
  await deleteValue(KEY_ID)
}

export const signChallenge = async (privateKey: CryptoKey, challenge: string) => {
  const data = new TextEncoder().encode(challenge)
  const signature = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', privateKey, data)
  return arrayBufferToBase64(signature)
}

const arrayBufferToBase64 = (buffer: ArrayBuffer) => {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (const byte of bytes) {
    binary += String.fromCharCode(byte)
  }
  return btoa(binary)
}
