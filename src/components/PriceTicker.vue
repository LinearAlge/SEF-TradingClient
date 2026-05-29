<script setup lang="ts">
type TickerItem = {
  symbol: string
  name: string
  price: string
  change: string
  tone: 'positive' | 'negative' | 'neutral'
}

const props = withDefaults(
  defineProps<{
    items?: TickerItem[]
  }>(),
  {
    items: () => [
      { symbol: '600001', name: '石英系统', price: '112.40', change: '+1.8%', tone: 'positive' },
      { symbol: '600002', name: '新星出行', price: '86.12', change: '-0.6%', tone: 'negative' },
      { symbol: '600003', name: '流明食品', price: '24.98', change: '+0.2%', tone: 'positive' },
      { symbol: '300001', name: '星河智能', price: '74.31', change: '+2.1%', tone: 'positive' },
    ],
  },
)

const emit = defineEmits<{
  (event: 'select', symbol: string): void
}>()
</script>

<template>
  <div class="card">
    <div class="card-title">市场脉动</div>
    <div class="card-subtitle">活跃标的实时快照</div>
    <ul class="ticker-list">
      <li v-for="item in props.items" :key="item.symbol" class="ticker-item" @click="emit('select', item.symbol)">
        <div>
          <div class="ticker-symbol">{{ item.symbol }}</div>
          <div class="ticker-name">{{ item.name }}</div>
        </div>
        <div class="ticker-metrics">
          <div class="ticker-price">{{ item.price }}</div>
          <div
            :class="
              item.tone === 'positive'
                ? 'tag-positive'
                : item.tone === 'negative'
                ? 'tag-negative'
                : 'price-flat'
            "
          >
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
  cursor: pointer;
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
