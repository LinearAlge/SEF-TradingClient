<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  value: string
  change?: string
  note?: string
  tone?: 'positive' | 'negative' | 'neutral'
}>()

const toneClass = computed(() => {
  if (props.tone === 'positive') return 'tag-positive'
  if (props.tone === 'negative') return 'tag-negative'
  return ''
})
</script>

<template>
  <div class="card stat-card">
    <div class="stat-header">
      <p class="stat-title">{{ title }}</p>
      <span v-if="change" :class="['stat-change', toneClass]">{{ change }}</span>
    </div>
    <div class="stat-value">{{ value }}</div>
    <p v-if="note" class="stat-note">{{ note }}</p>
  </div>
</template>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.stat-title {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  margin: 0;
}

.stat-change {
  font-size: 12px;
  font-weight: 600;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
}

.stat-note {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
}
</style>
