<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import PriceTicker from '../components/PriceTicker.vue'
import { addAlert, loadAlerts, saveAlerts } from '../utils/tradingLocalStore'

type AlertItem = {
  id: string
  symbol: string
  condition: string
  currentPrice: string
  triggerPrice: string
  status: '监控中' | '已暂停' | '已触发'
  lastTriggered: string
}

const alerts = ref<AlertItem[]>([])

const showCreate = ref(false)
const newSymbol = ref('')
const newCondition = ref('高于')
const newPrice = ref('')
const tickerItems = ref<{ symbol: string; name: string; price: string; change: string; tone: 'positive' | 'negative' | 'neutral' }[]>([])
const route = useRoute()

const handleCreate = () => {
  if (!newSymbol.value.trim() || !newPrice.value.trim()) return
  alerts.value = addAlert({
    id: `ALT-${Date.now()}`,
    symbol: newSymbol.value.trim(),
    condition: newCondition.value,
    currentPrice: '--',
    triggerPrice: newPrice.value.trim(),
    status: '监控中',
    lastTriggered: '--',
  })
  newSymbol.value = ''
  newPrice.value = ''
  showCreate.value = false
}

const toggleAlert = (item: AlertItem) => {
  item.status = item.status === '已暂停' ? '监控中' : '已暂停'
  saveAlerts(alerts.value)
}

const refreshPrices = async () => {
  const items = [...alerts.value]
  await Promise.all(
    items.map(async (item) => {
      try {
        const response = await fetch(
          `http://localhost:3004/stocks?symbol=${encodeURIComponent(item.symbol)}`,
        )
        const payload = await response.json().catch(() => ({}))
        if (response.ok && payload.ok) {
          item.currentPrice = Number(payload.stock?.lastPrice || 0).toFixed(2)
        }
      } catch (error) {
        // ignore
      }
    }),
  )
  alerts.value = items
  saveAlerts(items)
}

const refreshTicker = async () => {
  try {
    const response = await fetch('http://localhost:3004/stocks?board=主板')
    const payload = await response.json().catch(() => ({}))
    if (!response.ok || !payload.ok) {
      tickerItems.value = []
      return
    }

    tickerItems.value = (payload.stocks || []).slice(0, 4).map((item: { symbol: string; name: string; lastPrice: number }) => ({
      symbol: item.symbol,
      name: item.name,
      price: Number(item.lastPrice).toFixed(2),
      change: '--',
      tone: 'neutral' as const,
    }))
  } catch (error) {
    tickerItems.value = []
  }
}

const handleTickerSelect = (symbol: string) => {
  newSymbol.value = symbol
  showCreate.value = true
}

onMounted(() => {
  alerts.value = loadAlerts()
  if (alerts.value.length === 0) {
    alerts.value = addAlert({
      id: 'ALT-01',
      symbol: '600001',
      condition: '高于',
      currentPrice: '--',
      triggerPrice: '120.00',
      status: '监控中',
      lastTriggered: '--',
    })
  }
  if (typeof route.query.symbol === 'string') {
    newSymbol.value = route.query.symbol
    showCreate.value = true
  }
  refreshPrices()
  refreshTicker()
})
</script>

<template>
  <AppShell title="提醒" subtitle="价格触发提醒与监控状态" :showSearch="false">
    <template #actions>
      <button class="btn btn-primary" type="button" @click="showCreate = !showCreate">新增提醒</button>
    </template>

    <section class="layout-split">
      <div class="card">
        <div class="card-title">提醒列表</div>
        <div class="card-subtitle">条件、状态与触发记录</div>
        <div class="inline-actions alert-actions">
          <button class="btn btn-ghost btn-small" type="button">全部暂停</button>
          <button class="btn btn-ghost btn-small" type="button" @click="refreshPrices">刷新价格</button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>股票</th>
              <th>条件</th>
              <th class="numeric">当前价</th>
              <th class="numeric">触发价</th>
              <th>状态</th>
              <th>最近触发</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in alerts" :key="item.id">
              <td>{{ item.symbol }}</td>
              <td>{{ item.condition }}</td>
              <td class="numeric">{{ item.currentPrice }}</td>
              <td class="numeric">{{ item.triggerPrice }}</td>
              <td>
                <span
                  :class="[
                    'status-pill',
                    item.status === '已触发'
                      ? 'positive'
                      : item.status === '已暂停'
                      ? 'negative'
                      : 'neutral',
                  ]"
                >
                  {{ item.status }}
                </span>
              </td>
              <td>{{ item.lastTriggered }}</td>
              <td>
                <div class="inline-actions">
                  <button class="btn btn-small" type="button" @click="toggleAlert(item)">
                    {{ item.status === '已暂停' ? '恢复' : '暂停' }}
                  </button>
                  <button class="btn btn-ghost btn-small" type="button">编辑</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="grid">
        <div v-if="showCreate" class="card">
          <div class="card-title">新增提醒</div>
          <div class="card-subtitle">设置触发条件</div>
          <form class="form-grid" @submit.prevent="handleCreate">
            <label class="field">
              股票代码
              <input v-model="newSymbol" class="input" placeholder="例如 600001" />
            </label>
            <label class="field">
              条件
              <select v-model="newCondition" class="select">
                <option>高于</option>
                <option>低于</option>
              </select>
            </label>
            <label class="field">
              触发价格
              <input v-model="newPrice" class="input" placeholder="触发价" />
            </label>
            <button class="btn btn-primary" type="submit">保存提醒</button>
          </form>
        </div>
        <PriceTicker :items="tickerItems" @select="handleTickerSelect" />
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
.form-grid {
  display: grid;
  gap: 12px;
}

.alert-actions {
  margin-bottom: 12px;
}
</style>
