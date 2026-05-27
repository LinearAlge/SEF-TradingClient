<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  clearStoredKeyPair,
  ensureStoredKeyPair,
  loadStoredKeyPair,
  signChallenge,
} from '../utils/certificateStore'

const router = useRouter()
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

      router.push('/dashboard')
      return
    }

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
    <div class="login-left">
      <div class="login-brand">
        <span class="brand-dot"></span>
        栖木交易
      </div>
      <h1>清晰掌控交易。</h1>
      <p class="login-copy">
        在统一的交易客户端中查看资金、持仓与委托。
      </p>
      <div class="login-chips">
        <span class="chip">实时行情</span>
        <span class="chip">限价风控</span>
        <span class="chip">成交回执</span>
      </div>
      <div class="login-footnote">撮合引擎已就绪</div>
    </div>

    <div class="login-card card">
      <h2>登录</h2>
      <p class="card-subtitle">使用资金账户登录。</p>
      <form class="login-form" @submit.prevent="handleLogin">
        <label class="field">
          账户卡号
          <input v-model="account" class="input" placeholder="请输入账户卡号" />
        </label>
        <label class="field">
          交易密码
          <input v-model="password" class="input" type="password" placeholder="请输入交易密码" />
        </label>
        <label class="field">
          证书状态
          <input class="input" :value="certStatusText" readonly />
        </label>
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
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  padding: 48px 10vw;
  position: relative;
  z-index: 1;
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

.brand-dot {
  width: 14px;
  height: 14px;
  border-radius: 0;
  background: var(--accent);
}

.login-copy {
  font-size: 16px;
  color: var(--muted);
  max-width: 360px;
}

.login-chips {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.login-footnote {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.16em;
}

.login-card {
  max-width: 420px;
  align-self: center;
  padding: 28px;
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
  font-size: 40px;
  margin: 0;
}

h2 {
  margin: 0 0 6px;
}

@media (max-width: 720px) {
  .login {
    padding: 32px 20px;
  }

  h1 {
    font-size: 32px;
  }
}
</style>
