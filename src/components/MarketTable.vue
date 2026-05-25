<script setup lang="ts">
const stocks = [
  {
    symbol: 'QST',
<<<<<<< HEAD
    name: '石英系统',
=======
    name: 'Quartz Systems',
>>>>>>> origin/master
    last: '112.40',
    high: '118.20',
    low: '109.80',
    bid: '112.10',
    ask: '112.50',
    volume: '1.2M',
  },
  {
    symbol: 'NVA',
<<<<<<< HEAD
    name: '新星出行',
=======
    name: 'Nova Mobility',
>>>>>>> origin/master
    last: '86.12',
    high: '90.40',
    low: '84.60',
    bid: '86.05',
    ask: '86.20',
    volume: '780K',
  },
  {
    symbol: 'LUM',
<<<<<<< HEAD
    name: '流明食品',
=======
    name: 'Lumen Foods',
>>>>>>> origin/master
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
<<<<<<< HEAD
    <div class="card-title">行情看板</div>
    <div class="card-subtitle">买一卖一与价格区间</div>
    <table class="table">
      <thead>
        <tr>
          <th>代码</th>
          <th>最新价</th>
          <th>最高</th>
          <th>最低</th>
          <th>买一</th>
          <th>卖一</th>
          <th>成交量</th>
=======
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
>>>>>>> origin/master
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
