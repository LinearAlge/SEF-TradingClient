<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import FundsSummary from '../components/FundsSummary.vue'
import HoldingsTable from '../components/HoldingsTable.vue'
import { useTradingStore } from '../composables/useTradingStore'

const store = useTradingStore()
const refreshKey = ref(0)
const message = ref('')
const errorMessage = ref('')
const showDeposit = ref(false)
const showWithdraw = ref(false)
const depositAmount = ref('')
const withdrawAmount = ref('')
const withdrawPassword = ref('')

const cashFlows = computed(() => store.state.cashFlows)
const stockFlows = computed(() => store.state.stockFlows)
const availableFunds = computed(() => store.state.funds?.available ?? 0)

const refreshFlows = async () => {
  await Promise.all([store.refreshFlows(), store.refreshFunds(), store.refreshHoldings()])
  refreshKey.value += 1
}

const handleDeposit = async () => {
  message.value = ''
  errorMessage.value = ''
  const amount = Number(depositAmount.value)
  if (!amount || amount <= 0) {
    errorMessage.value = '存款金额必须大于 0'
    return
  }

  try {
    await store.deposit(amount)
    message.value = '存款成功'
    depositAmount.value = ''
    showDeposit.value = false
    refreshKey.value += 1
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '存款失败'
  }
}

const handleWithdraw = async () => {
  message.value = ''
  errorMessage.value = ''
  const amount = Number(withdrawAmount.value)
  if (!amount || amount <= 0) {
    errorMessage.value = '取款金额必须大于 0'
    return
  }
  if (amount > availableFunds.value) {
    errorMessage.value = '取款金额超过可用资金'
    return
  }

  try {
    await store.withdraw(amount, withdrawPassword.value || undefined)
    message.value = '取款申请成功'
    withdrawAmount.value = ''
    withdrawPassword.value = ''
    showWithdraw.value = false
    refreshKey.value += 1
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '取款失败'
  }
}

onMounted(async () => {
  const stored = localStorage.getItem('trading-account') || 'admin'
  store.setAccount(stored)
  await Promise.all([refreshFlows(), store.refreshWatchlist(), store.refreshPreferences()])
})
</script>

<template>
  <AppShell
    title="资产"
    subtitle="资金余额、冻结资金与持仓"
    :showSearch="false"
    :showRefresh="true"
    refreshLabel="刷新资产"
    :onRefresh="refreshFlows"
  >
    <template #actions>
      <button class="btn btn-ghost" type="button" @click="showWithdraw = !showWithdraw">取款</button>
      <button class="btn btn-primary" type="button" @click="showDeposit = !showDeposit">存款</button>
    </template>

    <section class="grid grid-2">
      <FundsSummary :refreshKey="refreshKey" />
      <HoldingsTable :refreshKey="refreshKey" />
    </section>

    <div v-if="showDeposit" class="card">
      <div class="card-title">存款</div>
      <div class="card-subtitle">输入入金金额</div>
      <div class="form-grid">
        <label class="field">
          金额
          <input v-model="depositAmount" class="input" placeholder="例如 10000" />
        </label>
        <button class="btn btn-primary" type="button" @click="handleDeposit">确认存款</button>
      </div>
    </div>

    <div v-if="showWithdraw" class="card">
      <div class="card-title">取款</div>
      <div class="card-subtitle">输入金额与取款密码</div>
      <div class="form-grid">
        <label class="field">
          金额
          <input v-model="withdrawAmount" class="input" placeholder="例如 5000" />
        </label>
        <label class="field">
          取款密码
          <input v-model="withdrawPassword" class="input" type="password" placeholder="可选" />
        </label>
        <button class="btn btn-primary" type="button" @click="handleWithdraw">确认取款</button>
      </div>
    </div>

    <div v-if="message" class="form-hint price-up">{{ message }}</div>
    <div v-if="errorMessage" class="form-hint price-down">{{ errorMessage }}</div>

    <section class="grid grid-2">
      <div class="card">
        <div class="card-title">资金流水</div>
        <div class="card-subtitle">买入冻结、撤单解冻与资金入账</div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>时间</th>
                <th>类型</th>
                <th class="numeric">金额</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in cashFlows" :key="item.id">
                <td>{{ item.time }}</td>
                <td>{{ item.type }}</td>
                <td class="numeric">{{ item.amount }}</td>
                <td><span class="status-pill positive">{{ item.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <div class="card-title">证券流水</div>
        <div class="card-subtitle">成交入股与卖出出股</div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>时间</th>
                <th>类型</th>
                <th>股票</th>
                <th class="numeric">数量</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in stockFlows" :key="item.id">
                <td>{{ item.time }}</td>
                <td>{{ item.type }}</td>
                <td>{{ item.symbol }}</td>
                <td class="numeric">{{ item.qty }}</td>
                <td><span class="status-pill positive">{{ item.status }}</span></td>
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
  gap: 12px;
}
</style>
