<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useTradingStore } from '../composables/useTradingStore'

const store = useTradingStore()
const alerts = computed(() => store.state.alerts)

onMounted(() => {
  const stored = localStorage.getItem('trading-account') || 'admin'
  store.setAccount(stored)
  store.refreshAlerts()
})
</script>

<template>
  <div class="card">
    <div class="card-title">价格提醒</div>
    <div class="card-subtitle">自定义触发条件</div>
    <ul class="alert-list">
      <li v-for="alert in alerts" :key="alert.id" class="alert-item">
        <div>
          <div class="alert-symbol">{{ alert.symbol }}</div>
          <div class="alert-trigger">{{ alert.condition }} {{ alert.triggerPrice }}</div>
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
  border-radius: 0;
  background: var(--color-bg-main);
}

.alert-symbol {
  font-weight: 700;
}

.alert-trigger {
  font-size: 12px;
  color: var(--muted);
}
</style>
