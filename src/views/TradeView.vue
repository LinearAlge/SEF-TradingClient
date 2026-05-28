<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import OrderListTable from '../components/OrderListTable.vue'
import { addOrder, loadOrders } from '../utils/tradingLocalStore'

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

const route = useRoute()
const side = ref<'buy' | 'sell'>((route.query.side as 'buy' | 'sell') || 'buy')
const symbol = ref((route.query.symbol as string) || '')
const price = ref('')
const quantity = ref('')
const note = ref('')
const preview = ref(false)
const errors = ref<string[]>([])
const submitMessage = ref('')

const availableFunds = ref(128420)
const availableShares = ref(1200)
const lastPrice = ref(118.53)
const stockName = ref('')
const stockStatus = ref('未知')

const limitUp = computed(() => Number((lastPrice.value * 1.1).toFixed(2)))
const limitDown = computed(() => Number((lastPrice.value * 0.9).toFixed(2)))

const maxBuyQuantity = computed(() => {
  const priceValue = Number(price.value)
  if (!priceValue) return 0
  return Math.floor(availableFunds.value / priceValue / 100) * 100
})

const canSubmit = computed(() => errors.value.length === 0)

const orders = ref<OrderItem[]>([])

const fetchStockSnapshot = async () => {
  if (!symbol.value.trim()) {
    stockName.value = ''
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

    stockName.value = payload.stock?.name || ''
    lastPrice.value = Number(payload.stock?.lastPrice || lastPrice.value)
    stockStatus.value = '正常'
  } catch (error) {
    stockStatus.value = '未知'
  }
}

const validate = () => {
  const issues: string[] = []
  const priceValue = Number(price.value)
  const qtyValue = Number(quantity.value)

  if (!symbol.value.trim()) issues.push('请输入股票代码')
  if (!priceValue || priceValue <= 0) issues.push('请输入有效委托价格')
  if (!qtyValue || qtyValue <= 0) issues.push('请输入有效委托数量')

  if (priceValue) {
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
  preview.value = validate()
}

const handleSubmit = () => {
  if (!validate()) {
    preview.value = false
    return
  }

  const order: OrderItem = {
    id: `ORD-${Date.now()}`,
    createdAt: new Date().toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit' }),
    symbol: symbol.value.trim(),
    name: stockName.value || '—',
    side: side.value === 'buy' ? '买入' : '卖出',
    price: Number(price.value),
    quantity: Number(quantity.value),
    filledQuantity: 0,
    status: '未成交',
  }
  orders.value = addOrder(order)
  submitMessage.value = '委托已提交，等待撮合。'
  preview.value = false
}

onMounted(() => {
  orders.value = loadOrders()
  fetchStockSnapshot()
})

watch(symbol, () => {
  fetchStockSnapshot()
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
      <button class="btn btn-ghost" type="button">查看委托</button>
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
          <div class="ticket-actions">
            <button class="btn btn-ghost" type="button" @click="handlePreview">预览</button>
            <button class="btn btn-primary" type="button" :disabled="!canSubmit" @click="handleSubmit">
              提交委托
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
