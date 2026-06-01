<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import OrderListTable from '../components/OrderListTable.vue'
import { useTradingStore } from '../composables/useTradingStore'

const store = useTradingStore()

const filters = ['全部', '可撤', '未成交', '部分成交', '已成交', '已撤单', '已拒绝']
const activeFilter = ref('全部')
const searchText = ref('')
const lastUpdated = ref('尚未刷新')
const actionMessage = ref('')
const actionError = ref('')
const selectedIds = ref<string[]>([])

const orders = computed(() => store.state.orders)
const fills = computed(() => store.state.fills)

const filteredOrders = computed(() => {
  let result = [...orders.value]
  if (activeFilter.value === '可撤') {
    result = result.filter((item) => ['未成交', '部分成交'].includes(item.status))
  } else if (activeFilter.value !== '全部') {
    result = result.filter((item) => item.status === activeFilter.value)
  }

  if (searchText.value.trim()) {
    const keyword = searchText.value.trim()
    result = result.filter((item) =>
      [item.id, item.symbol, item.name || ''].some((field) => field.includes(keyword)),
    )
  }
  return result
})

const handleSearch = (value: string) => {
  searchText.value = value
}

const toggleSelection = (order: typeof orders.value[number]) => {
  if (selectedIds.value.includes(order.id)) {
    selectedIds.value = selectedIds.value.filter((id) => id !== order.id)
  } else {
    selectedIds.value = [...selectedIds.value, order.id]
  }
}

const handleCancel = async (order: typeof orders.value[number]) => {
  actionMessage.value = ''
  actionError.value = ''
  try {
    await store.cancelOrder(order.id)
    actionMessage.value = `委托 ${order.id} 已撤单`
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : '撤单失败'
  }
}

const handleBatchCancel = async () => {
  actionMessage.value = ''
  actionError.value = ''
  const targetIds = selectedIds.value.length > 0 ? selectedIds.value : orders.value.map((item) => item.id)
  const cancellable = orders.value.filter(
    (item) => targetIds.includes(item.id) && ['未成交', '部分成交'].includes(item.status),
  )
  if (cancellable.length === 0) {
    actionError.value = '暂无可撤单的委托'
    return
  }

  try {
    for (const order of cancellable) {
      await store.cancelOrder(order.id)
    }
    actionMessage.value = '批量撤单完成'
    selectedIds.value = []
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : '批量撤单失败'
  }
}

const refreshOrders = async () => {
  await Promise.all([store.refreshOrders(), store.refreshFills()])
  lastUpdated.value = new Date().toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(async () => {
  const stored = localStorage.getItem('trading-account') || 'admin'
  store.setAccount(stored)
  store.connectOrderStream()
  await refreshOrders()
})
</script>

<template>
  <AppShell
    title="委托成交"
    subtitle="跟踪状态、撤单与成交回报"
    :showSearch="true"
    searchPlaceholder="搜索委托号或股票"
    :showRefresh="true"
    refreshLabel="刷新委托"
    :onRefresh="refreshOrders"
    :onSearch="handleSearch"
    :lastUpdated="lastUpdated"
    :statusItems="[
      { label: '当前资金账号', value: store.state.accountId },
      { label: '交易通道', value: store.state.wsStatus },
    ]"
  >
    <template #actions>
      <button class="btn btn-ghost" type="button" @click="handleBatchCancel">批量撤单</button>
    </template>

    <div class="order-filters">
      <button
        v-for="item in filters"
        :key="item"
        class="btn btn-small"
        type="button"
        :class="activeFilter === item ? 'btn-primary' : ''"
        @click="activeFilter = item"
      >
        {{ item }}
      </button>
    </div>

    <OrderListTable
      title="全部委托"
      subtitle="近 30 日记录"
      :items="filteredOrders"
      selectable
      :selectedIds="selectedIds"
      @toggle="toggleSelection"
      @cancel="handleCancel"
    />

    <div v-if="actionMessage" class="form-hint price-up">{{ actionMessage }}</div>
    <div v-if="actionError" class="form-hint price-down">{{ actionError }}</div>

    <div class="card">
      <div class="card-title">成交回报</div>
      <div class="card-subtitle">成交结果与回报明细</div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>时间</th>
              <th>委托号</th>
              <th>股票</th>
              <th>方向</th>
              <th class="numeric">成交价</th>
              <th class="numeric">成交量</th>
              <th class="numeric">成交金额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="fills.length === 0">
              <td colspan="7">暂无成交回报</td>
            </tr>
            <tr v-else v-for="item in fills" :key="item.id">
              <td>{{ item.createdAt }}</td>
              <td>{{ item.orderId }}</td>
              <td>{{ item.symbol }}</td>
              <td :class="item.side === '买入' ? 'price-up' : 'price-down'">{{ item.side }}</td>
              <td class="numeric">{{ item.price.toFixed(2) }}</td>
              <td class="numeric">{{ item.quantity }}</td>
              <td class="numeric">{{ (item.price * item.quantity).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppShell>
</template>

<style scoped>
.order-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
