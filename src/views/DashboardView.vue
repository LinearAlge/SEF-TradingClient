<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import StatCard from '../components/StatCard.vue'
import HoldingsTable from '../components/HoldingsTable.vue'
import OrderListTable from '../components/OrderListTable.vue'
import PriceTicker from '../components/PriceTicker.vue'
import { loadAlerts, loadFills, loadOrders } from '../utils/tradingLocalStore'

type FundsSnapshot = {
  available: number
  frozen: number
  marketValue: number
  totalEquity: number
  updatedAt?: string
}

const funds = ref<FundsSnapshot | null>(null)
const fundsError = ref('')
const tickerItems = ref<{ symbol: string; name: string; price: string; change: string; tone: 'positive' | 'negative' | 'neutral' }[]>([])
const refreshKey = ref(0)
const lastUpdated = ref('尚未刷新')

type OrderItem = {
  id: string
  createdAt: string
  symbol: string
  name?: string
  side: '买入' | '卖出'
  price: number
  quantity: number
  filledQuantity: number
  avgPrice?: number
  status: '未成交' | '部分成交' | '已成交' | '已撤单' | '已过期' | '已拒绝'
}

type FillItem = {
  id: string
  createdAt: string
  symbol: string
  side: '买入' | '卖出'
  price: number
  quantity: number
}

const latestOrders = ref<OrderItem[]>([])
const latestFills = ref<FillItem[]>([])
const todos = ref([
  { label: '未成交委托', value: 0 },
  { label: '部分成交', value: 0 },
  { label: '可撤单', value: 0 },
  { label: '已触发提醒', value: 0 },
])

const accountId = computed(() => localStorage.getItem('trading-account') || 'admin')

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

const fetchFunds = async () => {
  fundsError.value = ''
  try {
    const response = await fetch(
      `http://localhost:3003/funds?account=${encodeURIComponent(accountId.value)}`,
    )
    const payload = await response.json().catch(() => ({}))
    if (!response.ok || !payload.ok) {
      fundsError.value = payload.message || '资金信息加载失败'
      funds.value = null
      return
    }

    funds.value = payload
  } catch (error) {
    fundsError.value = '无法连接资金服务'
    funds.value = null
  }
}

const fetchTicker = async () => {
  try {
    const response = await fetch('http://localhost:3004/stocks?board=主板')
    const payload = await response.json().catch(() => ({}))
    if (!response.ok || !payload.ok) {
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

const loadWorkbenchData = () => {
  const orders = loadOrders()
  const fills = loadFills()
  const alerts = loadAlerts()
  latestOrders.value = orders.slice(0, 5)
  latestFills.value = fills.slice(0, 5)

  const pending = orders.filter((item) => item.status === '未成交').length
  const partial = orders.filter((item) => item.status === '部分成交').length
  const cancellable = orders.filter((item) => ['未成交', '部分成交'].includes(item.status)).length
  const triggered = alerts.filter((item) => item.status === '已触发').length
  todos.value = [
    { label: '未成交委托', value: pending },
    { label: '部分成交', value: partial },
    { label: '可撤单', value: cancellable },
    { label: '已触发提醒', value: triggered },
  ]
}

const refreshDashboard = () => {
  refreshKey.value += 1
  fetchFunds()
  loadWorkbenchData()
  fetchTicker()
  lastUpdated.value = new Date().toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  refreshDashboard()
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
  >
    <template #actions>
      <button class="btn btn-primary" type="button">新建委托</button>
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
