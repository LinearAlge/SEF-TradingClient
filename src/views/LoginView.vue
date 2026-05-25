<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const account = ref('')
const password = ref('')
const certificate = ref('主证书')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''
  if (!account.value.trim() || !password.value) {
    errorMessage.value = '请输入账户卡号和交易密码'
    return
  }

  loading.value = true
  try {
    const response = await fetch('http://localhost:3001/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        account: account.value.trim(),
        password: password.value,
        certificate: certificate.value,
      }),
    })

    const data = await response.json().catch(() => ({}))
    if (!response.ok || !data.ok) {
      errorMessage.value = data.message || '登录失败，请检查账号或密码'
      return
    }

    router.push('/dashboard')
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
          安全证书
          <select v-model="certificate" class="select">
            <option>主证书</option>
            <option>备用证书</option>
          </select>
        </label>
        <div class="login-actions">
          <button class="btn btn-ghost" type="button">申请权限</button>
          <button class="btn btn-primary" type="submit" :disabled="loading">
            {{ loading ? '登录中...' : '进入工作台' }}
          </button>
        </div>
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

.login-error {
  margin: 0;
  font-size: 12px;
  color: var(--accent-negative);
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
