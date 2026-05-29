<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { loadStoredKeyPair, signChallenge } from '../utils/certificateStore'
import { useTradingStore } from '../composables/useTradingStore'

const tradePassword = ref('')
const tradePasswordNext = ref('')
const tradePasswordConfirm = ref('')
const tradeMessage = ref('')

const cashPassword = ref('')
const cashPasswordNext = ref('')
const cashPasswordConfirm = ref('')
const cashMessage = ref('')

const store = useTradingStore()
const loginRecords = computed(() => store.state.loginRecords)
const certStatus = ref('本机已绑定')

const validatePassword = (current: string, next: string, confirm: string) => {
  if (!current || !next || !confirm) return '请完整填写密码信息'
  if (current === next) return '新旧密码不能相同'
  if (next.length < 6) return '密码长度至少 6 位'
  if (next !== confirm) return '两次输入的新密码不一致'
  return ''
}

const handleTradeSave = async () => {
  tradeMessage.value = validatePassword(tradePassword.value, tradePasswordNext.value, tradePasswordConfirm.value)
  if (tradeMessage.value) return
  try {
    await store.changeTradePassword({
      currentPassword: tradePassword.value,
      nextPassword: tradePasswordNext.value,
    })
    tradeMessage.value = '交易密码已更新'
  } catch (error) {
    tradeMessage.value = error instanceof Error ? error.message : '交易密码更新失败'
  }
}

const handleCashSave = async () => {
  cashMessage.value = validatePassword(cashPassword.value, cashPasswordNext.value, cashPasswordConfirm.value)
  if (cashMessage.value) return
  try {
    await store.changeWithdrawPassword({
      currentPassword: cashPassword.value,
      nextPassword: cashPasswordNext.value,
    })
    cashMessage.value = '取款密码已更新'
  } catch (error) {
    cashMessage.value = error instanceof Error ? error.message : '取款密码更新失败'
  }
}

const refreshLoginRecords = async () => {
  await store.refreshLoginRecords()
}

const refreshCertStatus = async () => {
  const stored = await loadStoredKeyPair()
  certStatus.value = stored ? '本机已绑定' : '本机未绑定'
}

const handleCertVerify = async () => {
  const stored = await loadStoredKeyPair()
  if (!stored) {
    certStatus.value = '本机未绑定'
    return
  }
  await signChallenge(stored.privateKey, 'ping')
  certStatus.value = '验证通过'
}

onMounted(() => {
  const stored = localStorage.getItem('trading-account') || 'admin'
  store.setAccount(stored)
  refreshLoginRecords()
  refreshCertStatus()
})
</script>

<template>
  <AppShell title="安全" subtitle="密码、证书与登录记录" :showSearch="false">
    <template #actions>
      <button class="btn btn-ghost" type="button" @click="handleCertVerify">验证证书</button>
    </template>

    <section class="grid grid-2">
      <div class="card">
        <div class="card-title">交易密码</div>
        <div class="card-subtitle">下单时必填</div>
        <form class="form-grid" @submit.prevent="handleTradeSave">
          <label class="field">
            当前密码
            <input v-model="tradePassword" class="input" type="password" placeholder="请输入当前密码" />
          </label>
          <label class="field">
            新密码
            <input v-model="tradePasswordNext" class="input" type="password" placeholder="请输入新密码" />
          </label>
          <label class="field">
            确认密码
            <input v-model="tradePasswordConfirm" class="input" type="password" placeholder="请再次输入新密码" />
          </label>
          <button class="btn btn-primary" type="submit">保存交易密码</button>
          <div v-if="tradeMessage" :class="tradeMessage.includes('已更新') ? 'price-up' : 'price-down'">
            {{ tradeMessage }}
          </div>
        </form>
      </div>
      <div class="card">
        <div class="card-title">取款密码</div>
        <div class="card-subtitle">取款时必填</div>
        <form class="form-grid" @submit.prevent="handleCashSave">
          <label class="field">
            当前密码
            <input v-model="cashPassword" class="input" type="password" placeholder="请输入当前密码" />
          </label>
          <label class="field">
            新密码
            <input v-model="cashPasswordNext" class="input" type="password" placeholder="请输入新密码" />
          </label>
          <label class="field">
            确认密码
            <input v-model="cashPasswordConfirm" class="input" type="password" placeholder="请再次输入新密码" />
          </label>
          <button class="btn btn-primary" type="submit">保存取款密码</button>
          <div v-if="cashMessage" :class="cashMessage.includes('已更新') ? 'price-up' : 'price-down'">
            {{ cashMessage }}
          </div>
        </form>
      </div>
    </section>

    <section class="grid grid-2">
      <div class="card cert-card">
        <div class="card-title">安全证书</div>
        <div class="card-subtitle">本机证书与验证状态</div>
        <div class="cert-body">
          <div class="cert-item">
            <span>证书状态</span>
            <strong>{{ certStatus }}</strong>
          </div>
          <div class="cert-item">
            <span>最近验证</span>
            <strong>今日 09:30</strong>
          </div>
        </div>
        <div class="inline-actions cert-actions">
          <button class="btn btn-ghost btn-small" type="button">重新绑定</button>
          <button class="btn btn-primary btn-small" type="button" @click="handleCertVerify">验证证书</button>
        </div>
      </div>
      <div class="card">
        <div class="card-title">登录记录</div>
        <div class="card-subtitle">最近 7 日访问</div>
        <div class="inline-actions record-actions">
          <button class="btn btn-ghost btn-small" type="button" @click="refreshLoginRecords">刷新记录</button>
        </div>
        <div class="record-scroll">
          <table class="table">
            <thead>
              <tr>
                <th>时间</th>
                <th>方式</th>
                <th>设备</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in loginRecords" :key="record.id">
                <td>{{ record.time }}</td>
                <td>{{ record.method }}</td>
                <td>{{ record.device }}</td>
                <td><span class="status-pill positive">{{ record.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
.form-grid {
  display: grid;
  gap: 14px;
}

.record-actions {
  margin-bottom: 12px;
}

.record-scroll {
  max-height: 240px;
  overflow-y: auto;
  overflow-x: hidden;
}

.cert-card {
  display: grid;
  gap: 10px;
}

.cert-body {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--color-border);
  background: #ffffff;
  font-size: 13px;
  color: var(--muted);
}

.cert-item {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.cert-item strong {
  color: var(--color-text-primary);
  font-weight: 600;
}

.cert-actions {
  margin-top: 2px;
}
</style>
