<script setup lang="ts">
const tickers = [
<<<<<<< HEAD
  { symbol: 'QST', name: '石英系统', price: '112.40', change: '+1.8%', tone: 'positive' },
  { symbol: 'NVA', name: '新星出行', price: '86.12', change: '-0.6%', tone: 'negative' },
  { symbol: 'LUM', name: '流明食品', price: '24.98', change: '+0.2%', tone: 'positive' },
  { symbol: 'SRF', name: '冲浪实验室', price: '74.31', change: '+2.1%', tone: 'positive' },
=======
  { symbol: 'QST', name: 'Quartz Systems', price: '112.40', change: '+1.8%', tone: 'positive' },
  { symbol: 'NVA', name: 'Nova Mobility', price: '86.12', change: '-0.6%', tone: 'negative' },
  { symbol: 'LUM', name: 'Lumen Foods', price: '24.98', change: '+0.2%', tone: 'positive' },
  { symbol: 'SRF', name: 'Surfer Labs', price: '74.31', change: '+2.1%', tone: 'positive' },
>>>>>>> origin/master
]
</script>

<template>
  <div class="card">
<<<<<<< HEAD
    <div class="card-title">市场脉动</div>
    <div class="card-subtitle">活跃标的实时快照</div>
=======
    <div class="card-title">Market Pulse</div>
    <div class="card-subtitle">Realtime snapshot of active symbols</div>
>>>>>>> origin/master
    <ul class="ticker-list">
      <li v-for="item in tickers" :key="item.symbol" class="ticker-item">
        <div>
          <div class="ticker-symbol">{{ item.symbol }}</div>
          <div class="ticker-name">{{ item.name }}</div>
        </div>
        <div class="ticker-metrics">
          <div class="ticker-price">{{ item.price }}</div>
          <div :class="item.tone === 'positive' ? 'tag-positive' : 'tag-negative'">
            {{ item.change }}
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.ticker-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ticker-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.ticker-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.ticker-symbol {
  font-weight: 700;
  font-size: 16px;
}

.ticker-name {
  font-size: 12px;
  color: var(--muted);
}

.ticker-metrics {
  text-align: right;
}

.ticker-price {
  font-size: 16px;
  font-weight: 600;
}
</style>
