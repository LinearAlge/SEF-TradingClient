<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
  }>(),
  {
<<<<<<< HEAD
    title: '委托',
    subtitle: '跨市场最新动态',
=======
    title: 'Orders',
    subtitle: 'Latest activity across markets',
>>>>>>> origin/master
  },
)

const orders = [
  {
    id: 'ORD-1024',
    symbol: 'QST',
<<<<<<< HEAD
    side: '买入',
    price: '112.20',
    qty: 300,
    status: '未成交',
=======
    side: 'Buy',
    price: '112.20',
    qty: 300,
    status: 'Open',
>>>>>>> origin/master
  },
  {
    id: 'ORD-1019',
    symbol: 'NVA',
<<<<<<< HEAD
    side: '卖出',
    price: '86.50',
    qty: 120,
    status: '部分成交',
=======
    side: 'Sell',
    price: '86.50',
    qty: 120,
    status: 'Partial',
>>>>>>> origin/master
  },
  {
    id: 'ORD-1013',
    symbol: 'LUM',
<<<<<<< HEAD
    side: '买入',
    price: '24.80',
    qty: 500,
    status: '已成交',
=======
    side: 'Buy',
    price: '24.80',
    qty: 500,
    status: 'Filled',
>>>>>>> origin/master
  },
  {
    id: 'ORD-1002',
    symbol: 'SRF',
<<<<<<< HEAD
    side: '卖出',
    price: '73.90',
    qty: 260,
    status: '已撤单',
=======
    side: 'Sell',
    price: '73.90',
    qty: 260,
    status: 'Canceled',
>>>>>>> origin/master
  },
]

const statusTone = (status: string) => {
<<<<<<< HEAD
  if (status === '已成交') return 'tag-positive'
  if (status === '已撤单') return 'tag-negative'
=======
  if (status === 'Filled') return 'tag-positive'
  if (status === 'Canceled') return 'tag-negative'
>>>>>>> origin/master
  return ''
}
</script>

<template>
  <div class="card">
    <div class="card-title">{{ props.title }}</div>
    <div class="card-subtitle">{{ props.subtitle }}</div>
    <table class="table">
      <thead>
        <tr>
<<<<<<< HEAD
          <th>委托号</th>
          <th>代码</th>
          <th>方向</th>
          <th>价格</th>
          <th>数量</th>
          <th>状态</th>
=======
          <th>Order</th>
          <th>Symbol</th>
          <th>Side</th>
          <th>Price</th>
          <th>Qty</th>
          <th>Status</th>
>>>>>>> origin/master
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in orders" :key="order.id">
          <td>{{ order.id }}</td>
          <td>{{ order.symbol }}</td>
          <td>{{ order.side }}</td>
          <td>{{ order.price }}</td>
          <td>{{ order.qty }}</td>
          <td :class="statusTone(order.status)">{{ order.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
