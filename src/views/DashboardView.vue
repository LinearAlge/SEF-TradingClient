<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import StatCard from '../components/StatCard.vue'
import HoldingsTable from '../components/HoldingsTable.vue'
import OrderListTable from '../components/OrderListTable.vue'
import PriceTicker from '../components/PriceTicker.vue'
import { useTradingStore } from '../composables/useTradingStore'
import { fetchStocks } from '../services/clientApi'

const store = useTradingStore()
const router = useRouter()

const tickerItems = ref<{
  symbol: string
  name: string
  price: string
  change: string
  tone: 'positive' | 'negative' | 'neutral'
}[]>([])
const refreshKey = ref(0)
const lastUpdated = ref('尚未刷新')
const wsStatus = computed(() => store.state.wsStatus)

const funds = computed(() => store.state.funds)
const fundsError = computed(() => store.state.error)
const latestOrders = computed(() => store.state.orders.slice(0, 5))
const latestFills = computed(() => store.state.fills.slice(0, 5))
const todos = computed(() => {
  const orders = store.state.orders
  const alerts = store.state.alerts
  const pending = orders.filter((item) => item.status === '未成交').length
  const partial = orders.filter((item) => item.status === '部分成交').length
  const cancellable = orders.filter((item) => ['未成交', '部分成交'].includes(item.status)).length
  const triggered = alerts.filter((item) => item.status === '已触发').length
  return [
    { label: '未成交委托', value: pending },
    { label: '部分成交', value: partial },
    { label: '可撤单', value: cancellable },
    { label: '已触发提醒', value: triggered },
  ]
})

const formatCurrency = (value?: number) => {
  if (value === undefined || value === null) {
    return '--'
  }

  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
  }).format(value)
}

const formatUpdatedAt = (value?: string) => {
  if (!value) {
    return '尚未刷新'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return '更新时间解析失败'
  }

  return `更新于 ${date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })}`
}

const formatNumber = (value?: number) => {
  if (value === undefined || value === null) return '--'
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

const fetchTicker = async () => {
  try {
    const payload = await fetchStocks({ board: '主板' })
    if (!payload.ok) {
      tickerItems.value = []
      return
    }

    const items = (payload.stocks || []).slice(0, 4).map((item: { symbol: string; name: string; lastPrice: number }) => ({
      symbol: item.symbol,
      name: item.name,
      price: formatNumber(item.lastPrice),
      change: '--',
      tone: 'neutral' as const,
    }))
    tickerItems.value = items
  } catch (error) {
    tickerItems.value = []
  }
}

const refreshDashboard = async () => {
  refreshKey.value += 1
  await Promise.all([
    store.refreshFunds(),
    store.refreshHoldings(),
    store.refreshOrders(),
    store.refreshFills(),
    store.refreshAlerts(),
  ])
  await fetchTicker()
  lastUpdated.value = new Date().toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })
}

const openTrade = () => {
  router.push('/trade')
}

onMounted(async () => {
  const stored = localStorage.getItem('trading-account') || 'admin'
  store.setAccount(stored)
  store.connectOrderStream()
  await Promise.all([refreshDashboard(), store.refreshWatchlist(), store.refreshPreferences()])
})
</script>

<template>
  <AppShell
    title="首页"
    subtitle="资金、持仓与委托任务一览"
    :showSearch="false"
    :showRefresh="true"
    refreshLabel="刷新本页"
    :onRefresh="refreshDashboard"
    :lastUpdated="lastUpdated"
    :statusItems="[
      { label: '当前资金账号', value: store.state.accountId },
      { label: '交易通道', value: wsStatus },
    ]"
  >
    <template #actions>
      <button class="btn btn-primary" type="button" @click="openTrade">新建委托</button>
    </template>

    <section class="metric-strip">
      <StatCard
        title="可用资金"
        :value="formatCurrency(funds?.available)"
        :note="fundsError || formatUpdatedAt(funds?.updatedAt)"
        density="compact"
      />
      <StatCard
        title="冻结资金"
        :value="formatCurrency(funds?.frozen)"
        :note="fundsError || '未成交委托占用'"
        density="compact"
      />
      <StatCard
        title="证券市值"
        :value="formatCurrency(funds?.marketValue)"
        :note="fundsError || '持仓最新估值'"
        density="compact"
      />
      <StatCard
        title="资产总值"
        :value="formatCurrency(funds?.totalEquity)"
        :note="fundsError || '资金与市值合计'"
        density="compact"
      />
    </section>

    <section class="layout-split">
      <HoldingsTable :refreshKey="refreshKey" />
      <div class="grid">
        <div class="card">
          <div class="card-title">今日待办</div>
          <div class="card-subtitle">需要处理的委托与提醒</div>
          <div class="todo-grid">
            <div v-for="item in todos" :key="item.label" class="todo-item">
              <div class="todo-label">{{ item.label }}</div>
              <div class="todo-value">{{ item.value }}</div>
            </div>
          </div>
        </div>
        <PriceTicker :items="tickerItems" />
      </div>
    </section>

    <section class="grid grid-2">
      <div class="card">
        <div class="card-title">最新委托</div>
        <div class="card-subtitle">近 1 小时委托状态</div>
        <OrderListTable :items="latestOrders" compact />
      </div>
      <div class="card">
        <div class="card-title">最新成交</div>
        <div class="card-subtitle">成交回报与执行情况</div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>时间</th>
                <th>股票</th>
                <th>方向</th>
                <th class="numeric">成交价</th>
                <th class="numeric">成交量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="latestFills.length === 0">
                <td colspan="5">暂无成交记录</td>
              </tr>
              <tr v-else v-for="item in latestFills" :key="item.id">
                <td>{{ item.createdAt }}</td>
                <td>{{ item.symbol }}</td>
                <td :class="item.side === '买入' ? 'price-up' : 'price-down'">{{ item.side }}</td>
                <td class="numeric">{{ formatNumber(item.price) }}</td>
                <td class="numeric">{{ item.quantity }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
.todo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.todo-item {
  border: 1px solid var(--color-border);
  padding: 10px 12px;
  background: #ffffff;
}

.todo-label {
  font-size: 12px;
  color: var(--muted);
}

.todo-value {
  margin-top: 6px;
  font-size: 18px;
  font-weight: 700;
}
</style>
