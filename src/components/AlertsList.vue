<script setup lang="ts">
const alerts = [
  {
    symbol: 'QST',
    trigger: 'Price above 115.00',
    status: 'Monitoring',
  },
  {
    symbol: 'NVA',
    trigger: 'Price below 84.50',
    status: 'Monitoring',
  },
  {
    symbol: 'LUM',
    trigger: 'Volume spike over 3M',
    status: 'Paused',
  },
]
</script>

<template>
  <div class="card">
    <div class="card-title">Price Alerts</div>
    <div class="card-subtitle">Optional reminders for key levels</div>
    <ul class="alert-list">
      <li v-for="alert in alerts" :key="alert.symbol" class="alert-item">
        <div>
          <div class="alert-symbol">{{ alert.symbol }}</div>
          <div class="alert-trigger">{{ alert.trigger }}</div>
        </div>
        <span class="chip">{{ alert.status }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.alert-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(244, 162, 97, 0.12);
}

.alert-symbol {
  font-weight: 700;
}

.alert-trigger {
  font-size: 12px;
  color: var(--muted);
}
</style>
