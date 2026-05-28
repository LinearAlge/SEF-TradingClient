<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

type HoldingItem = {
  symbol: string
  name: string
  shares: number
  costPrice: number
  lastPrice: number
  pnlAmount: number
  pnlRate: number
}

const holdings = ref<HoldingItem[]>([])
const loading = ref(false)
const errorMessage = ref('')
const asOf = ref('')
const totalMarketValue = ref(0)
const now = ref(Date.now())

let clockTimer: ReturnType<typeof setInterval> | null = null

const accountId = computed(() => localStorage.getItem('trading-account') || 'admin')

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
  }).format(value)

const formatRate = (value: number) => `${(value * 100).toFixed(2)}%`

const asOfLabel = computed(() => {
  if (!asOf.value) {
    return '尚未刷新'
  }

  const asOfDate = new Date(asOf.value)
  if (Number.isNaN(asOfDate.getTime())) {
    return '更新时间解析失败'
  }

  const timeText = asOfDate.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })
  const diffMinutes = Math.max(0, Math.floor((now.value - asOfDate.getTime()) / 60000))
  let relative = diffMinutes <= 0 ? '刚刚' : `${diffMinutes}分钟前`
  if (diffMinutes >= 60) {
    relative = `${Math.floor(diffMinutes / 60)}小时前`
  }

  return `更新于 ${timeText}（${relative}）`
})

const fetchHoldings = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(
      `http://localhost:3002/holdings?account=${encodeURIComponent(accountId.value)}`,
    )
    const data = await response.json().catch(() => ({}))
    if (!response.ok || !data.ok) {
      errorMessage.value = data.message || '持仓数据加载失败'
      holdings.value = []
      return
    }

    holdings.value = data.holdings || []
    asOf.value = data.asOf || ''
    totalMarketValue.value = data.totalMarketValue || 0
  } catch (error) {
    errorMessage.value = '无法连接持仓服务'
    holdings.value = []
  } finally {
    loading.value = false
    now.value = Date.now()
  }
}

onMounted(() => {
  fetchHoldings()
  clockTimer = setInterval(() => {
    now.value = Date.now()
  }, 60000)
})

onUnmounted(() => {
  if (clockTimer) {
    clearInterval(clockTimer)
  }
})
</script>

<template>
  <div class="card">
    <div class="card-header">
      <div>
        <div class="card-title">持仓</div>
        <div class="card-subtitle">证券账户关联持仓</div>
        <div class="meta-row">
          <span class="sub-meta">{{ asOfLabel }}</span>
        </div>
      </div>
      <button class="btn btn-ghost btn-small" type="button" :disabled="loading" @click="fetchHoldings">
        手动刷新
      </button>
    </div>
    <div class="summary" v-if="totalMarketValue">
      总市值：{{ formatCurrency(totalMarketValue) }}
    </div>
    <table class="table">
      <thead>
        <tr>
          <th>代码</th>
          <th>股数</th>
          <th>成本</th>
          <th>最新价</th>
          <th>盈亏</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="5">加载中...</td>
        </tr>
        <tr v-else-if="errorMessage">
          <td colspan="5">{{ errorMessage }}</td>
        </tr>
        <tr v-else-if="holdings.length === 0">
          <td colspan="5">暂无持仓</td>
        </tr>
        <tr v-else v-for="item in holdings" :key="item.symbol">
          <td>
            <div class="symbol">{{ item.symbol }}</div>
            <div class="name">{{ item.name }}</div>
          </td>
          <td>{{ item.shares }}</td>
          <td>{{ formatCurrency(item.costPrice) }}</td>
          <td>{{ formatCurrency(item.lastPrice) }}</td>
          <td :class="item.pnlAmount < 0 ? 'tag-negative' : 'tag-positive'">
            {{ formatCurrency(item.pnlAmount) }} ({{ formatRate(item.pnlRate) }})
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.meta-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.summary {
  font-size: 13px;
  margin-bottom: 12px;
  color: var(--muted);
}

.sub-meta {
  font-size: 12px;
  color: var(--muted);
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.symbol {
  font-weight: 600;
}

.name {
  font-size: 12px;
  color: var(--muted);
}
</style>
