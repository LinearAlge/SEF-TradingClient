<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

type FundsData = {
  available: number
  frozen: number
  marketValue: number
  totalEquity: number
  updatedAt?: string
}

const data = ref<FundsData | null>(null)
const loading = ref(false)
const errorMessage = ref('')
const now = ref(Date.now())

let clockTimer: ReturnType<typeof setInterval> | null = null

const accountId = computed(() => localStorage.getItem('trading-account') || 'admin')

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
  }).format(value)

const metrics = computed(() => {
  if (!data.value) {
    return []
  }

  return [
    {
      label: '可用资金',
      value: formatCurrency(data.value.available),
      note: '用于新买入委托',
    },
    {
      label: '冻结资金',
      value: formatCurrency(data.value.frozen),
      note: '用于未成交委托',
    },
    {
      label: '证券市值',
      value: formatCurrency(data.value.marketValue),
      note: '持仓最新估值',
    },
    {
      label: '总资产',
      value: formatCurrency(data.value.totalEquity),
      note: '资金与市值合计',
    },
  ]
})

const updatedAtLabel = computed(() => {
  if (!data.value?.updatedAt) {
    return '尚未刷新'
  }

  const updatedAt = new Date(data.value.updatedAt)
  if (Number.isNaN(updatedAt.getTime())) {
    return '更新时间解析失败'
  }

  const timeText = updatedAt.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })
  const diffMinutes = Math.max(0, Math.floor((now.value - updatedAt.getTime()) / 60000))
  let relative = diffMinutes <= 0 ? '刚刚' : `${diffMinutes}分钟前`
  if (diffMinutes >= 60) {
    relative = `${Math.floor(diffMinutes / 60)}小时前`
  }

  return `更新于 ${timeText}（${relative}）`
})

const fetchFunds = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(
      `http://localhost:3003/funds?account=${encodeURIComponent(accountId.value)}`,
    )
    const payload = await response.json().catch(() => ({}))
    if (!response.ok || !payload.ok) {
      errorMessage.value = payload.message || '资金数据加载失败'
      data.value = null
      return
    }

    data.value = payload
  } catch (error) {
    errorMessage.value = '无法连接资金服务'
    data.value = null
  } finally {
    loading.value = false
    now.value = Date.now()
  }
}

const props = defineProps<{
  refreshKey?: number
}>()

onMounted(() => {
  fetchFunds()
  clockTimer = setInterval(() => {
    now.value = Date.now()
  }, 60000)
})

watch(
  () => props.refreshKey,
  () => {
    fetchFunds()
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
        <div class="card-title">资金概览</div>
        <div class="card-subtitle">结算资金账户</div>
        <div class="meta-row">
          <span class="sub-meta">{{ updatedAtLabel }}</span>
        </div>
      </div>
      <span class="form-hint">页面刷新资产后更新</span>
    </div>
    <div class="metrics">
      <div v-if="loading" class="metric">加载中...</div>
      <div v-else-if="errorMessage" class="metric">{{ errorMessage }}</div>
      <div v-else v-for="item in metrics" :key="item.label" class="metric">
        <div class="metric-label">{{ item.label }}</div>
        <div class="metric-value">{{ item.value }}</div>
        <div class="metric-note">{{ item.note }}</div>
      </div>
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

.metrics {
  display: grid;
  gap: 14px;
}

.metric {
  padding: 12px 14px;
  border-radius: 0;
  background: var(--color-bg-main);
}

.sub-meta {
  font-size: 12px;
  color: var(--muted);
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.metric-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
  margin-top: 6px;
}

.metric-note {
  font-size: 12px;
  color: var(--muted);
  margin-top: 4px;
}
</style>
