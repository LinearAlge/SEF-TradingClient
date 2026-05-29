<script setup lang="ts">
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

const props = withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
    items?: ReadonlyArray<OrderItem>
    compact?: boolean
    selectable?: boolean
    selectedIds?: string[]
  }>(),
  {
    title: '委托',
    subtitle: '跨市场最新动态',
    items: () => [],
    compact: false,
    selectable: false,
    selectedIds: () => [],
  },
)

const emit = defineEmits<{
  (event: 'cancel', order: OrderItem): void
  (event: 'toggle', order: OrderItem): void
}>()

const statusTone = (status: OrderItem['status']) => {
  if (status === '已成交') return 'status-pill positive'
  if (status === '已撤单' || status === '已拒绝') return 'status-pill negative'
  if (status === '部分成交' || status === '未成交') return 'status-pill neutral'
  return 'status-pill neutral'
}

const canCancel = (status: OrderItem['status']) =>
  status === '未成交' || status === '部分成交'

const formatNumber = (value?: number) => {
  if (value === undefined || value === null) return '--'
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

const formatQuantity = (value?: number) => (value === undefined ? '--' : value.toString())
</script>

<template>
  <div class="card">
    <div class="card-title">{{ props.title }}</div>
    <div class="card-subtitle">{{ props.subtitle }}</div>
    <div class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>委托号</th>
            <th>时间</th>
            <th>股票</th>
            <th>方向</th>
            <th class="numeric">委托价</th>
            <th class="numeric">委托量</th>
            <th v-if="!compact" class="numeric">已成交</th>
            <th v-if="!compact" class="numeric">未成交</th>
            <th v-if="!compact" class="numeric">成交均价</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="props.items.length === 0">
            <td :colspan="compact ? 8 : 11">暂无委托记录</td>
          </tr>
          <tr
            v-else
            v-for="order in props.items"
            :key="order.id"
            :class="{ 'is-selected': props.selectedIds.includes(order.id) }"
            @click="props.selectable ? emit('toggle', order) : undefined"
          >
            <td>{{ order.id }}</td>
            <td>{{ order.createdAt }}</td>
            <td>
              <div class="symbol">{{ order.symbol }}</div>
              <div class="name">{{ order.name || '--' }}</div>
            </td>
            <td :class="order.side === '买入' ? 'price-up' : 'price-down'">{{ order.side }}</td>
            <td class="numeric">{{ formatNumber(order.price) }}</td>
            <td class="numeric">{{ formatQuantity(order.quantity) }}</td>
            <td v-if="!compact" class="numeric">{{ formatQuantity(order.filledQuantity) }}</td>
            <td v-if="!compact" class="numeric">
              {{ formatQuantity(order.quantity - order.filledQuantity) }}
            </td>
            <td v-if="!compact" class="numeric">{{ formatNumber(order.avgPrice) }}</td>
            <td><span :class="statusTone(order.status)">{{ order.status }}</span></td>
            <td>
              <div class="inline-actions">
                <button
                  v-if="canCancel(order.status)"
                  class="btn btn-danger btn-small"
                  type="button"
                  @click.stop="emit('cancel', order)"
                >
                  撤单
                </button>
                <span v-else class="form-hint">--</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.symbol {
  font-weight: 600;
}

.name {
  font-size: 12px;
  color: var(--muted);
}
</style>
