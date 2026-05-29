<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import StockSearchPanel from '../components/StockSearchPanel.vue'
import MarketTable from '../components/MarketTable.vue'
import StockDetailCard from '../components/StockDetailCard.vue'
import PriceTicker from '../components/PriceTicker.vue'
import { fetchStock, fetchStocks as fetchMarketStocks } from '../services/clientApi'

type StockRow = {
  symbol: string
  name: string
  lastPrice: number
  dayHigh: number
  dayLow: number
  bid: number
  ask: number
  volume: number
}

type StockDetail = StockRow & {
  board: string
  weekHigh: number
  weekLow: number
  monthHigh: number
  monthLow: number
  announcements: string[]
}

const stocks = ref<StockRow[]>([])
const selected = ref<StockDetail | null>(null)
const selectedSymbol = ref('')
const loading = ref(false)
const errorMessage = ref('')
const detailLoading = ref(false)
const detailError = ref('')
const asOf = ref('')
const now = ref(Date.now())
let clockTimer: number | undefined
let refreshTimer: number | undefined
const router = useRouter()
const autoRefresh = ref<'manual' | 'auto'>('manual')
const currentQuery = ref('')
const currentBoard = ref('主板')

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
  const relative = diffMinutes <= 0 ? '刚刚' : `${diffMinutes}分钟前`
  return `更新于 ${timeText}（${relative}）`
})

const lastUpdatedLabel = computed(() => {
  if (!asOf.value) return '尚未刷新'
  return asOfLabel.value
})

const fetchStocks = async (query = '', board = '') => {
  currentQuery.value = query
  currentBoard.value = board
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await fetchMarketStocks({ query, board })
    if (!data.ok) {
      errorMessage.value = data.message || '行情加载失败'
      stocks.value = []
      selected.value = null
      return
    }

    stocks.value = data.stocks || []
    asOf.value = data.asOf || ''
    now.value = Date.now()
    if (stocks.value.length > 0 && stocks.value[0]) {
      await fetchStockDetail(stocks.value[0].symbol)
    } else {
      selected.value = null
    }
  } catch (error) {
    errorMessage.value = '无法连接行情服务'
    stocks.value = []
    selected.value = null
  } finally {
    loading.value = false
  }
}

const fetchStockDetail = async (symbol: string) => {
  detailLoading.value = true
  detailError.value = ''
  selectedSymbol.value = symbol
  try {
    const data = await fetchStock(symbol)
    if (!data.ok) {
      detailError.value = data.message || '股票详情加载失败'
      selected.value = null
      return
    }

    selected.value = data.stock || null
  } catch (error) {
    detailError.value = '无法连接行情服务'
    selected.value = null
  } finally {
    detailLoading.value = false
  }
}

const handleSearch = (payload: { query: string; board: string }) => {
  fetchStocks(payload.query, payload.board)
}

const handleReset = () => {
  fetchStocks('', '主板')
}

const handleRefresh = () => {
  fetchStocks(currentQuery.value, currentBoard.value)
}


const handleBuy = (symbol: string) => {
  router.push({ path: '/trade', query: { symbol, side: 'buy' } })
}

const handleSell = (symbol: string) => {
  router.push({ path: '/trade', query: { symbol, side: 'sell' } })
}

const handleAlert = (symbol: string) => {
  router.push({ path: '/alerts', query: { symbol } })
}

const tickerItems = computed(() =>
  stocks.value.slice(0, 4).map((item) => ({
    symbol: item.symbol,
    name: item.name,
    price: new Intl.NumberFormat('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(item.lastPrice),
    change: '--',
    tone: 'neutral' as const,
  })),
)

const startAutoRefresh = () => {
  if (refreshTimer) return
  refreshTimer = window.setInterval(() => {
    fetchStocks(currentQuery.value, currentBoard.value)
  }, 5000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = undefined
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = autoRefresh.value === 'auto' ? 'manual' : 'auto'
}

onMounted(() => {
  const query = typeof router.currentRoute.value.query.q === 'string' ? router.currentRoute.value.query.q : ''
  fetchStocks(query, '主板')
  clockTimer = window.setInterval(() => {
    now.value = Date.now()
  }, 60000)
})

watch(
  () => router.currentRoute.value.query.q,
  (next) => {
    if (typeof next === 'string') {
      fetchStocks(next, '主板')
    }
  },
)

watch(autoRefresh, (mode) => {
  if (mode === 'auto') {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

onUnmounted(() => {
  if (clockTimer) {
    clearInterval(clockTimer)
  }
  stopAutoRefresh()
})
</script>

<template>
  <AppShell
    title="行情中心"
    subtitle="最新成交、买一卖一与区间"
    :showSearch="false"
    :showRefresh="true"
    refreshLabel="刷新行情"
    :lastUpdated="lastUpdatedLabel"
    :onRefresh="handleRefresh"
  >
    <template #actions>
      <button class="btn btn-ghost" type="button" @click="toggleAutoRefresh">
        自动刷新：{{ autoRefresh === 'auto' ? '开' : '关' }}
      </button>
    </template>

    <StockSearchPanel @search="handleSearch" @reset="handleReset" />

    <section class="grid grid-2">
      <MarketTable
        :stocks="stocks"
        :loading="loading"
        :error="errorMessage"
        :asOfLabel="asOfLabel"
        :selectedSymbol="selectedSymbol"
        @select="fetchStockDetail"
        @buy="handleBuy"
        @sell="handleSell"
        @alert="handleAlert"
      />
      <div class="grid">
        <StockDetailCard :stock="selected" :loading="detailLoading" :error="detailError" :asOfLabel="asOfLabel" />
        <PriceTicker :items="tickerItems" @select="fetchStockDetail" />
      </div>
    </section>
  </AppShell>
</template>
