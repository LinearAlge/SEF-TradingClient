<script setup lang="ts">
const holdings = [
  {
    symbol: 'QST',
    name: '石英系统',
    shares: 860,
    cost: '104.32',
    last: '112.40',
    pnl: '+6.7%',
  },
  {
    symbol: 'NVA',
    name: '新星出行',
    shares: 420,
    cost: '88.10',
    last: '86.12',
    pnl: '-2.2%',
  },
  {
    symbol: 'LUM',
    name: '流明食品',
    shares: 1200,
    cost: '23.80',
    last: '24.98',
    pnl: '+5.0%',
  },
]
</script>

<template>
  <div class="card">
    <div class="card-title">持仓</div>
    <div class="card-subtitle">证券账户关联持仓</div>
    <table class="table">
      <thead>
        <tr>
          <th>代码</th>
          <th>股数</th>
          <th>成本</th>
          <th>最新价</th>
          <th>盈亏</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in holdings" :key="item.symbol">
          <td>
            <div class="symbol">{{ item.symbol }}</div>
            <div class="name">{{ item.name }}</div>
          </td>
          <td>{{ item.shares }}</td>
          <td>{{ item.cost }}</td>
          <td>{{ item.last }}</td>
          <td :class="item.pnl.startsWith('-') ? 'tag-negative' : 'tag-positive'">{{ item.pnl }}</td>
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
