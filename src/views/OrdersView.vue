<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import OrderListTable from '../components/OrderListTable.vue'
import { loadFills, loadOrders, updateOrderStatus } from '../utils/tradingLocalStore'

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

type FillItem = {
  id: string
  createdAt: string
  orderId: string
  symbol: string
  side: '买入' | '卖出'
  price: number
  quantity: number
}

const filters = ['全部', '可撤', '未成交', '部分成交', '已成交', '已撤单', '已过期']
const activeFilter = ref('全部')
const orders = ref<OrderItem[]>([])
const fills = ref<FillItem[]>([])
const searchText = ref('')
const lastUpdated = ref('尚未刷新')

const filteredOrders = computed(() => {
  let result = orders.value
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

const handleCancel = (order: OrderItem) => {
  const target = orders.value.find((item) => item.id === order.id)
  if (target && (target.status === '未成交' || target.status === '部分成交')) {
    orders.value = updateOrderStatus(target.id, '已撤单')
  }
}

onMounted(() => {
  orders.value = loadOrders()
  fills.value = loadFills()
  lastUpdated.value = new Date().toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })
})

const refreshOrders = () => {
  orders.value = loadOrders()
  fills.value = loadFills()
  lastUpdated.value = new Date().toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })
}
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
    :onSearch="(value) => { searchText.value = value }"
    :lastUpdated="lastUpdated"
  >
    <template #actions>
      <button class="btn btn-ghost" type="button">批量撤单</button>
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

    <OrderListTable title="全部委托" subtitle="近 30 日记录" :items="filteredOrders" @cancel="handleCancel" />

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
