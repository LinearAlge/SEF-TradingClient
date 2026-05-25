<script setup lang="ts">
const stocks = [
  {
    symbol: 'QST',
    name: 'Quartz Systems',
    last: '112.40',
    high: '118.20',
    low: '109.80',
    bid: '112.10',
    ask: '112.50',
    volume: '1.2M',
  },
  {
    symbol: 'NVA',
    name: 'Nova Mobility',
    last: '86.12',
    high: '90.40',
    low: '84.60',
    bid: '86.05',
    ask: '86.20',
    volume: '780K',
  },
  {
    symbol: 'LUM',
    name: 'Lumen Foods',
    last: '24.98',
    high: '25.70',
    low: '24.10',
    bid: '24.96',
    ask: '25.02',
    volume: '2.4M',
  },
]
</script>

<template>
  <div class="card">
    <div class="card-title">Market Board</div>
    <div class="card-subtitle">Best bid, best ask, and price bands</div>
    <table class="table">
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Last</th>
          <th>High</th>
          <th>Low</th>
          <th>Bid</th>
          <th>Ask</th>
          <th>Volume</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in stocks" :key="item.symbol">
          <td>
            <div class="symbol">{{ item.symbol }}</div>
            <div class="name">{{ item.name }}</div>
          </td>
          <td>{{ item.last }}</td>
          <td>{{ item.high }}</td>
          <td>{{ item.low }}</td>
          <td>{{ item.bid }}</td>
          <td>{{ item.ask }}</td>
          <td>{{ item.volume }}</td>
        </tr>
      </tbody>
    </table>
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
