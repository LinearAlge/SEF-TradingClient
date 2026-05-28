<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

type HoldingItem = {
  symbol: string
  name: string
  shares: number
  availableShares?: number
  frozenShares?: number
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

const props = defineProps<{
  refreshKey?: number
}>()

const accountId = computed(() => localStorage.getItem('trading-account') || 'admin')

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
  }).format(value)

const formatRate = (value: number) => `${(value * 100).toFixed(2)}%`

const formatNumber = (value?: number) => (value === undefined ? '--' : value.toString())

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

watch(
  () => props.refreshKey,
  () => {
    fetchHoldings()
  },
)

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
      <span class="form-hint">页面刷新资产后更新</span>
    </div>
    <div class="summary" v-if="totalMarketValue">
      总市值：{{ formatCurrency(totalMarketValue) }}
    </div>
    <div class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>代码</th>
            <th class="numeric">持仓</th>
            <th class="numeric">可卖</th>
            <th class="numeric">冻结</th>
            <th class="numeric">成本价</th>
            <th class="numeric">最新价</th>
            <th class="numeric">市值</th>
            <th class="numeric">盈亏</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="9">加载中...</td>
          </tr>
          <tr v-else-if="errorMessage">
            <td colspan="9">{{ errorMessage }}</td>
          </tr>
          <tr v-else-if="holdings.length === 0">
            <td colspan="9">暂无持仓</td>
          </tr>
          <tr v-else v-for="item in holdings" :key="item.symbol">
            <td>
              <div class="symbol">{{ item.symbol }}</div>
              <div class="name">{{ item.name }}</div>
            </td>
            <td class="numeric">{{ formatNumber(item.shares) }}</td>
            <td class="numeric">{{ formatNumber(item.availableShares) }}</td>
            <td class="numeric">{{ formatNumber(item.frozenShares) }}</td>
            <td class="numeric">{{ formatCurrency(item.costPrice) }}</td>
            <td class="numeric">{{ formatCurrency(item.lastPrice) }}</td>
            <td class="numeric">{{ formatCurrency(item.lastPrice * item.shares) }}</td>
            <td class="numeric" :class="item.pnlAmount < 0 ? 'tag-negative' : 'tag-positive'">
              {{ formatCurrency(item.pnlAmount) }} ({{ formatRate(item.pnlRate) }})
            </td>
            <td>
              <div class="inline-actions">
                <button class="btn btn-small" type="button">买入</button>
                <button class="btn btn-small" type="button">卖出</button>
                <button class="btn btn-ghost btn-small" type="button">提醒</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
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
