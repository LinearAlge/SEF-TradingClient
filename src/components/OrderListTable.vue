<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
  }>(),
  {
    title: 'Orders',
    subtitle: 'Latest activity across markets',
  },
)

const orders = [
  {
    id: 'ORD-1024',
    symbol: 'QST',
    side: 'Buy',
    price: '112.20',
    qty: 300,
    status: 'Open',
  },
  {
    id: 'ORD-1019',
    symbol: 'NVA',
    side: 'Sell',
    price: '86.50',
    qty: 120,
    status: 'Partial',
  },
  {
    id: 'ORD-1013',
    symbol: 'LUM',
    side: 'Buy',
    price: '24.80',
    qty: 500,
    status: 'Filled',
  },
  {
    id: 'ORD-1002',
    symbol: 'SRF',
    side: 'Sell',
    price: '73.90',
    qty: 260,
    status: 'Canceled',
  },
]

const statusTone = (status: string) => {
  if (status === 'Filled') return 'tag-positive'
  if (status === 'Canceled') return 'tag-negative'
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
          <th>Order</th>
          <th>Symbol</th>
          <th>Side</th>
          <th>Price</th>
          <th>Qty</th>
          <th>Status</th>
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
