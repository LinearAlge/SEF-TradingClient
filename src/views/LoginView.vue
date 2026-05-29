<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  clearStoredKeyPair,
  ensureStoredKeyPair,
  loadStoredKeyPair,
  signChallenge,
} from '../utils/certificateStore'
import { useTradingStore } from '../composables/useTradingStore'

const router = useRouter()
const store = useTradingStore()
const account = ref('')
const password = ref('')
const phone = ref('')
const idNumber = ref('')
const loading = ref(false)
const errorMessage = ref('')
const infoMessage = ref('')
const certStatus = ref('')
const showRebind = ref(false)

const certStatusText = computed(() => certStatus.value || '未检测到证书')

const updateCertStatus = async () => {
  const stored = await loadStoredKeyPair()
  certStatus.value = stored ? '本机证书已绑定' : '本机未绑定证书'
}

onMounted(() => {
  updateCertStatus()
})

const requestJson = async (path: string, payload: Record<string, unknown>) => {
  const response = await fetch(`http://localhost:3001${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  const data = await response.json().catch(() => ({}))
  return { response, data }
}

const handleLogin = async () => {
  errorMessage.value = ''
  infoMessage.value = ''
  if (!account.value.trim() || !password.value) {
    errorMessage.value = '请输入账户卡号和交易密码'
    return
  }

  loading.value = true
  try {
    const { response, data } = await requestJson('/login', {
      account: account.value.trim(),
      password: password.value,
    })

    if (!response.ok || !data.ok) {
      errorMessage.value = data.message || '登录失败，请检查账号或密码'
      return
    }

    if (data.action === 'enroll') {
      const { publicJwk } = await ensureStoredKeyPair()
      await updateCertStatus()
      const enrollResult = await requestJson('/enroll', {
        account: account.value.trim(),
        publicKey: publicJwk,
      })

      if (!enrollResult.response.ok || !enrollResult.data.ok) {
        errorMessage.value = enrollResult.data.message || '证书绑定失败'
        return
      }

      localStorage.setItem('trading-account', account.value.trim())
      store.setAccount(account.value.trim())
      await store.recordLogin({ method: '证书登录', device: 'Windows 终端', status: '成功' })
      router.push('/dashboard')
      return
    }

    if (data.action === 'verify') {
      const stored = await loadStoredKeyPair()
      if (!stored) {
        showRebind.value = true
        errorMessage.value = '当前设备未检测到证书，请重新绑定'
        return
      }

      const signature = await signChallenge(stored.privateKey, data.challenge)
      const verifyResult = await requestJson('/verify', {
        account: account.value.trim(),
        signature,
      })

      if (!verifyResult.response.ok || !verifyResult.data.ok) {
        errorMessage.value = verifyResult.data.message || '证书验证失败'
        return
      }

      localStorage.setItem('trading-account', account.value.trim())
      store.setAccount(account.value.trim())
      await store.recordLogin({ method: '证书登录', device: 'Windows 终端', status: '成功' })
      router.push('/dashboard')
      return
    }

    localStorage.setItem('trading-account', account.value.trim())
    store.setAccount(account.value.trim())
    await store.recordLogin({ method: '密码登录', device: 'Windows 终端', status: '成功' })
    router.push('/dashboard')
  } catch (error) {
    errorMessage.value = '无法连接测试服务，请确认后端已启动'
  } finally {
    loading.value = false
  }
}

const handleRebind = async () => {
  errorMessage.value = ''
  infoMessage.value = ''
  if (!account.value.trim() || !password.value || !phone.value.trim() || !idNumber.value.trim()) {
    errorMessage.value = '请输入账户、密码、手机号与身份证号'
    return
  }

  loading.value = true
  try {
    const { response, data } = await requestJson('/rebind', {
      account: account.value.trim(),
      password: password.value,
      phone: phone.value.trim(),
      idNumber: idNumber.value.trim(),
    })

    if (!response.ok || !data.ok) {
      errorMessage.value = data.message || '重新绑定失败'
      return
    }

    await clearStoredKeyPair()
    await updateCertStatus()
    infoMessage.value = '证书已重置，请重新登录以绑定新证书'
  } catch (error) {
    errorMessage.value = '无法连接测试服务，请确认后端已启动'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <div class="login-overlay"></div>
    <div class="login-shell">
      <div class="login-left">
        <div class="login-brand">
          <img class="brand-icon" src="/favicon.ico" alt="App" />
          新宇交易
        </div>
        <h1>统一交易工作台</h1>
        <h2 class="login-headline">资金、持仓与委托实时掌控</h2>
        <p class="login-copy">
          通过资金账户与本机证书完成身份校验，进入后可查看资金余额、证券持仓、
          实时行情与委托进度，并完成买入、卖出、撤单和提醒管理。
        </p>
        <div class="login-features">
          <div class="feature-card">
            <div class="feature-title">资金与持仓</div>
            <div class="feature-desc">查看可用资金、冻结资金、证券市值与持仓盈亏。</div>
          </div>
          <div class="feature-card">
            <div class="feature-title">行情与提醒</div>
            <div class="feature-desc">查询最新价、买一卖一、价格区间，并设置价格提醒。</div>
          </div>
          <div class="feature-card">
            <div class="feature-title">委托与成交</div>
            <div class="feature-desc">提交买卖委托，跟踪未成交、部分成交、已成交与撤单状态。</div>
          </div>
        </div>
        <div class="login-status">行情连接正常 · 交易通道正常 · 本机证书校验</div>
      </div>

      <div class="login-card card">
        <h2>登录</h2>
        <p class="card-subtitle">账户卡号 + 交易密码 + 证书状态。</p>
        <form class="login-form" @submit.prevent="handleLogin">
          <label class="field">
            账户卡号
            <input v-model="account" class="input" placeholder="请输入账户卡号" />
          </label>
          <label class="field">
            交易密码
            <input v-model="password" class="input" type="password" placeholder="请输入交易密码" />
          </label>
          <div class="cert-row">
            <div class="cert-label">证书状态</div>
            <div class="cert-value">
              <span class="status-pill neutral">{{ certStatusText }}</span>
            </div>
          </div>
          <div v-if="certStatusText.includes('未绑定')" class="form-hint">
            首次登录将为本机绑定安全证书。
          </div>
          <div v-else class="form-hint">正在验证本机证书。</div>
          <div class="login-actions">
            <button class="btn btn-ghost" type="button">申请权限</button>
            <button class="btn btn-primary" type="submit" :disabled="loading">
              {{ loading ? '登录中...' : '进入工作台' }}
            </button>
          </div>
          <div class="rebind-actions">
            <button class="btn btn-ghost" type="button" @click="showRebind = !showRebind">
              {{ showRebind ? '取消重新绑定' : '重新绑定证书' }}
            </button>
          </div>
          <div v-if="showRebind" class="rebind-panel">
            <label class="field">
              手机号
              <input v-model="phone" class="input" placeholder="请输入开户手机号" />
            </label>
            <label class="field">
              身份证号
              <input v-model="idNumber" class="input" placeholder="请输入身份证号" />
            </label>
            <button class="btn btn-primary" type="button" :disabled="loading" @click="handleRebind">
              {{ loading ? '处理中...' : '确认重新绑定' }}
            </button>
          </div>
          <p v-if="infoMessage" class="login-info">{{ infoMessage }}</p>
          <p v-if="errorMessage" class="login-error">{{ errorMessage }}</p>
        </form>
      </div>
    </div>
  </div>
</template>
<style scoped>
.login {
  min-height: 100vh;
  height: 100svh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 10vw;
  background: url('/Background.png') center / cover no-repeat;
  overflow: hidden;
}

:global(.app-root) {
  padding-bottom: 0;
}

.login-overlay {
  position: absolute;
  inset: 0;
  background: rgba(244, 245, 246, 0.5);
  /* backdrop-filter: blur(1px); */
}

.login-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(280px, 1.1fr) minmax(320px, 0.9fr);
  gap: 40px;
  width: min(1100px, 100%);
}

.login-left {
  display: flex;
  flex-direction: column;
  gap: 18px;
  justify-content: center;
}

.login-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.brand-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
}

.login-headline {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--muted);
}

.login-copy {
  font-size: 15px;
  color: var(--muted);
  max-width: 520px;
  line-height: 1.6;
}

.login-features {
  display: grid;
  gap: 12px;
}

.feature-card {
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.85);
  padding: 12px 14px;
}

.feature-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.feature-desc {
  font-size: 13px;
  color: var(--muted);
  margin-top: 6px;
}

.login-status {
  font-size: 12px;
  color: var(--muted);
}

.login-card {
  max-width: 460px;
  align-self: center;
  padding: 28px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 12px 24px -18px rgba(0, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.95);
}

.login-form {
  display: grid;
  gap: 14px;
}

.login-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.rebind-actions {
  display: flex;
  justify-content: flex-end;
}

.rebind-panel {
  display: grid;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--color-border-dark);
  background: #ffffff;
}

.login-error {
  margin: 0;
  font-size: 12px;
  color: var(--accent-negative);
}

.login-info {
  margin: 0;
  font-size: 12px;
  color: var(--accent-positive);
}

.login-actions .btn[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

h1 {
  font-size: 36px;
  margin: 0;
}

h2 {
  margin: 0 0 6px;
}

.cert-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  background: #ffffff;
}

.cert-label {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.cert-value {
  font-size: 12px;
}

@media (max-width: 720px) {
  .login {
    padding: 24px 16px;
    height: 100svh;
  }

  .login-shell {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 32px;
  }
}
</style>
