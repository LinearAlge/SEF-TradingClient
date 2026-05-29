<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import PriceTicker from '../components/PriceTicker.vue'
import { useTradingStore } from '../composables/useTradingStore'

const store = useTradingStore()
const alerts = computed(() => store.state.alerts)
const showCreate = ref(false)
const newSymbol = ref('')
const newCondition = ref('高于')
const newPrice = ref('')
const tickerItems = ref<{ symbol: string; name: string; price: string; change: string; tone: 'positive' | 'negative' | 'neutral' }[]>([])
const route = useRoute()
const actionMessage = ref('')
const actionError = ref('')

const handleCreate = async () => {
  actionMessage.value = ''
  actionError.value = ''
  if (!newSymbol.value.trim() || !newPrice.value.trim()) {
    actionError.value = '请填写股票代码与触发价'
    return
  }
  try {
    await store.createAlert({
      symbol: newSymbol.value.trim(),
      condition: newCondition.value,
      triggerPrice: newPrice.value.trim(),
    })
    newSymbol.value = ''
    newPrice.value = ''
    showCreate.value = false
    actionMessage.value = '提醒已保存'
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : '提醒创建失败'
  }
}

const toggleAlert = async (item: typeof alerts.value[number]) => {
  actionMessage.value = ''
  actionError.value = ''
  const nextStatus = item.status === '已暂停' ? '监控中' : '已暂停'
  try {
    await store.updateAlert(item.id, { status: nextStatus })
    actionMessage.value = nextStatus === '已暂停' ? '提醒已暂停' : '提醒已恢复'
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : '更新提醒失败'
  }
}

const removeAlert = async (item: typeof alerts.value[number]) => {
  actionMessage.value = ''
  actionError.value = ''
  try {
    await store.deleteAlert(item.id)
    actionMessage.value = '提醒已删除'
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : '删除提醒失败'
  }
}

const refreshPrices = async () => {
  const items = alerts.value.map((item) => ({ ...item }))
  await Promise.all(
    items.map(async (item) => {
      try {
        const response = await fetch(
          `http://localhost:3004/stocks?symbol=${encodeURIComponent(item.symbol)}`,
        )
        const payload = await response.json().catch(() => ({}))
        if (response.ok && payload.ok) {
          item.currentPrice = Number(payload.stock?.lastPrice || 0).toFixed(2)
          const current = Number(item.currentPrice)
          const trigger = Number(item.triggerPrice)
          if (item.status === '监控中') {
            if (item.condition === '高于' && current >= trigger) {
              item.status = '已触发'
              item.lastTriggered = new Date().toLocaleString('zh-CN', { hour12: false })
            }
            if (item.condition === '低于' && current <= trigger) {
              item.status = '已触发'
              item.lastTriggered = new Date().toLocaleString('zh-CN', { hour12: false })
            }
          }
        }
      } catch (error) {
        // ignore
      }
    }),
  )

  await Promise.all(items.map((item) => store.updateAlert(item.id, item)))
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

const pauseAll = async () => {
  actionMessage.value = ''
  actionError.value = ''
  try {
    await Promise.all(
      alerts.value
        .filter((item) => item.status === '监控中')
        .map((item) => store.updateAlert(item.id, { status: '已暂停' })),
    )
    actionMessage.value = '已暂停所有提醒'
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : '批量暂停失败'
  }
}

onMounted(async () => {
  const stored = localStorage.getItem('trading-account') || 'admin'
  store.setAccount(stored)
  await store.refreshAlerts()
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
          <button class="btn btn-ghost btn-small" type="button" @click="pauseAll">全部暂停</button>
          <button class="btn btn-ghost btn-small" type="button" @click="refreshPrices">刷新价格</button>
        </div>
        <div v-if="actionMessage" class="form-hint price-up">{{ actionMessage }}</div>
        <div v-if="actionError" class="form-hint price-down">{{ actionError }}</div>
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
                  <button class="btn btn-ghost btn-small" type="button" @click="removeAlert(item)">删除</button>
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
