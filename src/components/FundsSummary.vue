<script setup lang="ts">
const metrics = [
  {
    label: 'Available Cash',
    value: '$128,420',
    note: 'Ready for new buy orders',
  },
  {
    label: 'Frozen Funds',
    value: '$18,600',
    note: 'Reserved for open orders',
  },
  {
    label: 'Total Equity',
    value: '$412,890',
    note: 'Cash plus market value',
  },
]
</script>

<template>
  <div class="card">
    <div class="card-title">Funds Summary</div>
    <div class="card-subtitle">Linked settlement account</div>
    <div class="metrics">
      <div v-for="item in metrics" :key="item.label" class="metric">
        <div class="metric-label">{{ item.label }}</div>
        <div class="metric-value">{{ item.value }}</div>
        <div class="metric-note">{{ item.note }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.metrics {
  display: grid;
  gap: 14px;
}

.metric {
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(31, 122, 93, 0.08);
}

.metric-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
  margin-top: 6px;
}

.metric-note {
  font-size: 12px;
  color: var(--muted);
  margin-top: 4px;
}
</style>
