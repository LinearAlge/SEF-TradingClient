<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTradingStore } from '../composables/useTradingStore'

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

const store = useTradingStore()
const holdings = computed(() => store.state.holdings)
const loading = computed(() => store.state.loading.holdings)
const errorMessage = computed(() => store.state.error)
const asOf = computed(() => store.state.holdingsMeta.asOf)
const totalMarketValue = computed(() => store.state.holdingsMeta.totalMarketValue)
const now = ref(Date.now())

let clockTimer: ReturnType<typeof setInterval> | null = null

const props = defineProps<{
  refreshKey?: number
}>()

const router = useRouter()

const accountId = computed(() => localStorage.getItem('trading-account') || 'admin')
const watchlist = computed(() => store.state.watchlist)
const isWatchlisted = (symbol: string) => watchlist.value.includes(symbol)

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

onMounted(() => {
  const stored = localStorage.getItem('trading-account') || 'admin'
  store.setAccount(stored)
  store.refreshHoldings()
  clockTimer = setInterval(() => {
    now.value = Date.now()
  }, 60000)
})

watch(
  () => props.refreshKey,
  () => {
    store.refreshHoldings()
  },
)

onUnmounted(() => {
  if (clockTimer) {
    clearInterval(clockTimer)
  }
})

const goTrade = (symbol: string, side: 'buy' | 'sell') => {
  router.push({ path: '/trade', query: { symbol, side } })
}

const goAlert = (symbol: string) => {
  router.push({ path: '/alerts', query: { symbol } })
}

const toggleWatchlist = async (symbol: string) => {
  await store.toggleWatchlist(symbol)
}
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
                <button class="btn btn-small" type="button" @click="goTrade(item.symbol, 'buy')">买入</button>
                <button class="btn btn-small" type="button" @click="goTrade(item.symbol, 'sell')">卖出</button>
                <button class="btn btn-ghost btn-small" type="button" @click="goAlert(item.symbol)">提醒</button>
                <button class="btn btn-ghost btn-small" type="button" @click="toggleWatchlist(item.symbol)">
                  {{ isWatchlisted(item.symbol) ? '已自选' : '自选' }}
                </button>
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
