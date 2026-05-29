<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import OrderListTable from '../components/OrderListTable.vue'
import { useTradingStore } from '../composables/useTradingStore'

const route = useRoute()
const router = useRouter()
const store = useTradingStore()

const side = ref<'buy' | 'sell'>((route.query.side as 'buy' | 'sell') || 'buy')
const symbol = ref((route.query.symbol as string) || '')
const price = ref('')
const quantity = ref('')
const note = ref('')
const preview = ref(false)
const errors = ref<string[]>([])
const submitMessage = ref('')
const submitError = ref('')
const loading = ref(false)

const stockName = ref('')
const stockStatus = ref('未知')
const lastPrice = ref(0)
const bidPrice = ref(0)
const askPrice = ref(0)
const maxBuyQuantity = ref(0)
const availableShares = ref(0)

const accountId = computed(() => store.state.accountId)
const availableFunds = computed(() => store.availableFunds.value)

const limitUp = computed(() => (lastPrice.value ? Number((lastPrice.value * 1.1).toFixed(2)) : 0))
const limitDown = computed(() => (lastPrice.value ? Number((lastPrice.value * 0.9).toFixed(2)) : 0))
const canSubmit = computed(() => errors.value.length === 0 && !loading.value)

const orders = computed(() => store.state.orders)

const fetchStockSnapshot = async () => {
  if (!symbol.value.trim()) {
    stockName.value = ''
    stockStatus.value = '未知'
    lastPrice.value = 0
    bidPrice.value = 0
    askPrice.value = 0
    return
  }

  try {
    const response = await fetch(
      `http://localhost:3004/stocks?symbol=${encodeURIComponent(symbol.value.trim())}`,
    )
    const payload = await response.json().catch(() => ({}))
    if (!response.ok || !payload.ok) {
      stockName.value = ''
      stockStatus.value = '未知'
      return
    }

    const stock = payload.stock || {}
    stockName.value = stock.name || ''
    lastPrice.value = Number(stock.lastPrice || 0)
    bidPrice.value = Number(stock.bid || 0)
    askPrice.value = Number(stock.ask || 0)
    stockStatus.value = '正常'

    if (!price.value) {
      if (side.value === 'buy') {
        price.value = (askPrice.value || lastPrice.value || 0).toFixed(2)
      } else {
        price.value = (bidPrice.value || lastPrice.value || 0).toFixed(2)
      }
    }
  } catch (error) {
    stockStatus.value = '未知'
  }
}

const refreshLimits = () => {
  const priceValue = Number(price.value)
  if (!priceValue) {
    maxBuyQuantity.value = 0
  } else {
    maxBuyQuantity.value = Math.floor(availableFunds.value / priceValue / 100) * 100
  }

  if (symbol.value) {
    const holding = store.holdingsMap.value.get(symbol.value)
    availableShares.value = holding?.availableShares ?? 0
  } else {
    availableShares.value = 0
  }
}

const validate = () => {
  const issues: string[] = []
  const priceValue = Number(price.value)
  const qtyValue = Number(quantity.value)

  if (!symbol.value.trim()) issues.push('请输入股票代码')
  if (!stockName.value) issues.push('股票不存在')
  if (!priceValue || priceValue <= 0) issues.push('请输入有效委托价格')
  if (!qtyValue || qtyValue <= 0) issues.push('请输入有效委托数量')
  if (qtyValue && qtyValue % 100 !== 0) issues.push('委托数量需为 100 的整数倍')

  if (priceValue && lastPrice.value) {
    if (priceValue > limitUp.value || priceValue < limitDown.value) {
      issues.push('委托价格超出涨跌停范围')
    }
  }

  if (side.value === 'buy') {
    if (priceValue && qtyValue && priceValue * qtyValue > availableFunds.value) {
      issues.push('委托金额超过可用资金')
    }
  } else {
    if (qtyValue > availableShares.value) {
      issues.push('委托数量超过可卖数量')
    }
  }

  errors.value = issues
  return issues.length === 0
}

const handlePreview = () => {
  submitMessage.value = ''
  submitError.value = ''
  preview.value = validate()
}

const handleSubmit = async () => {
  if (!validate()) {
    preview.value = false
    return
  }

  loading.value = true
  submitMessage.value = ''
  submitError.value = ''
  try {
    const order = await store.placeOrder({
      symbol: symbol.value.trim(),
      side: side.value === 'buy' ? '买入' : '卖出',
      price: Number(price.value),
      quantity: Number(quantity.value),
      note: note.value.trim(),
    })
    submitMessage.value = `委托已提交，编号 ${order.id}，状态 ${order.status}`
    preview.value = false
    refreshLimits()
  } catch (error) {
    submitError.value = error instanceof Error ? error.message : '委托提交失败'
  } finally {
    loading.value = false
  }
}

const openOrders = () => {
  router.push('/orders')
}

onMounted(async () => {
  const stored = localStorage.getItem('trading-account') || 'admin'
  store.setAccount(stored)
  await Promise.all([store.refreshFunds(), store.refreshHoldings(), store.refreshOrders()])
  await fetchStockSnapshot()
  refreshLimits()
})

watch(symbol, async () => {
  await fetchStockSnapshot()
  refreshLimits()
})

watch([price, () => store.state.funds], () => {
  refreshLimits()
})

watch(
  () => route.query,
  (next) => {
    if (typeof next.side === 'string') {
      side.value = next.side === 'sell' ? 'sell' : 'buy'
    }
    if (typeof next.symbol === 'string') {
      symbol.value = next.symbol
    }
  },
)
</script>

<template>
  <AppShell title="交易" subtitle="提交买卖委托与风控校验" :showSearch="false">
    <template #actions>
      <button class="btn btn-ghost" type="button" @click="openOrders">查看委托</button>
    </template>

    <section class="layout-split">
      <div class="card">
        <div class="card-title">委托输入</div>
        <div class="card-subtitle">买入/卖出切换与委托预览</div>
        <div class="segmented">
          <button
            class="btn btn-small"
            type="button"
            :class="side === 'buy' ? 'btn-primary' : ''"
            @click="side = 'buy'"
          >
            买入
          </button>
          <button
            class="btn btn-small"
            type="button"
            :class="side === 'sell' ? 'btn-primary' : ''"
            @click="side = 'sell'"
          >
            卖出
          </button>
        </div>
        <form class="ticket-form" @submit.prevent>
          <label class="field">
            股票代码
            <input v-model="symbol" class="input" placeholder="例如 600001" />
          </label>
          <div class="meta-row">
            <span>股票名称：{{ stockName || '--' }}</span>
            <span>状态：{{ stockStatus }}</span>
          </div>
          <label class="field">
            委托类型
            <input class="input" value="限价" readonly />
          </label>
          <label class="field">
            委托价格
            <input v-model="price" class="input" placeholder="输入价格" />
          </label>
          <label class="field">
            委托数量
            <input v-model="quantity" class="input" placeholder="100" />
          </label>
          <label class="field">
            有效期
            <input class="input" value="当日有效" readonly />
          </label>
          <label class="field">
            备注
            <textarea v-model="note" class="textarea" rows="3" placeholder="可选备注"></textarea>
          </label>
          <div class="form-hint">
            买入可用资金 {{ availableFunds }} 元 · 卖出可用数量 {{ availableShares }} 股
          </div>
          <div v-if="errors.length" class="form-hint price-down">
            {{ errors.join('，') }}
          </div>
          <div v-if="submitError" class="form-hint price-down">{{ submitError }}</div>
          <div class="ticket-actions">
            <button class="btn btn-ghost" type="button" @click="handlePreview">预览</button>
            <button class="btn btn-primary" type="button" :disabled="!canSubmit" @click="handleSubmit">
              {{ loading ? '提交中...' : '提交委托' }}
            </button>
          </div>
        </form>
        <div v-if="preview" class="preview-panel">
          <div class="card-title">委托预览</div>
          <div class="preview-row">方向：{{ side === 'buy' ? '买入' : '卖出' }}</div>
          <div class="preview-row">股票：{{ symbol || '--' }}</div>
          <div class="preview-row">价格：{{ price || '--' }}</div>
          <div class="preview-row">数量：{{ quantity || '--' }}</div>
          <div class="preview-row">预计冻结：{{ side === 'buy' ? '资金' : '股票' }}</div>
        </div>
        <div v-if="submitMessage" class="form-hint price-up">{{ submitMessage }}</div>
      </div>
      <div class="grid">
        <div class="card">
          <div class="card-title">当前行情</div>
          <div class="card-subtitle">最新价与价格边界</div>
          <div class="metric-strip">
            <div class="metric">
              <div class="metric-label">最新价</div>
              <div class="metric-value">{{ lastPrice }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">涨停价</div>
              <div class="metric-value">{{ limitUp }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">跌停价</div>
              <div class="metric-value">{{ limitDown }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">买一 / 卖一</div>
              <div class="metric-value">{{ bidPrice || '--' }} / {{ askPrice || '--' }}</div>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-title">账户约束</div>
          <div class="card-subtitle">可买/可卖与资金占用</div>
          <div class="metric-strip">
            <div class="metric">
              <div class="metric-label">可用资金</div>
              <div class="metric-value">{{ availableFunds }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">可买数量</div>
              <div class="metric-value">{{ maxBuyQuantity }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">可卖数量</div>
              <div class="metric-value">{{ availableShares }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <OrderListTable title="当前委托" subtitle="待撮合的委托" :items="orders" compact />
  </AppShell>
</template>

<style scoped>
.segmented {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.ticket-form {
  display: grid;
  gap: 12px;
}

.ticket-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.preview-panel {
  border: 1px solid var(--color-border);
  padding: 12px;
  margin-top: 12px;
  background: #ffffff;
}

.preview-row {
  font-size: 13px;
  margin-top: 6px;
}
</style>
