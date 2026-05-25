<script setup lang="ts">
const metrics = [
  {
    label: '可用资金',
    value: '$128,420',
    note: '用于新买入委托',
  },
  {
    label: '冻结资金',
    value: '$18,600',
    note: '用于未成交委托',
  },
  {
    label: '总资产',
    value: '$412,890',
    note: '现金与市值合计',
  },
]
</script>

<template>
  <div class="card">
<<<<<<< HEAD
    <div class="card-title">资金概览</div>
    <div class="card-subtitle">结算资金账户</div>
=======
    <div class="card-title">Funds Summary</div>
    <div class="card-subtitle">Linked settlement account</div>
>>>>>>> origin/master
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
  border-radius: 0;
  background: var(--color-bg-main);
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
