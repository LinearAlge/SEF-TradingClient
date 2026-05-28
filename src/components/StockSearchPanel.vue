<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['search', 'reset', 'filters-change'])

const query = ref('')
const board = ref('主板')
const range = ref('今日')

const filters = ['今日', '本周', '本月']

const handleSearch = () => {
  emit('search', {
    query: query.value.trim(),
    board: board.value,
    range: range.value,
  })
}

const handleReset = () => {
  query.value = ''
  board.value = '主板'
  range.value = '今日'
  emit('reset')
}

const notifyFilters = () => {
  emit('filters-change', {
    range: range.value,
  })
}

const handleEnter = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleSearch()
  }
}
</script>

<template>
  <div class="card search-panel">
    <div>
      <div class="card-title">股票查询</div>
      <div class="card-subtitle">查看最高最低、买一卖一</div>
    </div>
    <div class="search-grid">
      <label class="field">
        代码或名称
        <input
          v-model="query"
          class="input"
          placeholder="例如 600001 或 石英"
          @keyup="handleEnter"
        />
      </label>
      <label class="field">
        交易板块
        <select v-model="board" class="select">
          <option>主板</option>
          <option>创业板</option>
          <option>ST 板</option>
        </select>
      </label>
      <div class="search-actions inline-actions">
        <button class="btn btn-primary" type="button" @click="handleSearch">查询</button>
        <button class="btn btn-ghost" type="button" @click="handleReset">重置</button>
      </div>
    </div>
    <div class="filter-row chips">
      <span
        v-for="item in filters"
        :key="item"
        :class="['chip', range === item ? 'chip-active' : '']"
        @click="range = item; notifyFilters()"
      >
        {{ item }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.search-panel {
  display: grid;
  gap: 16px;
}

.search-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.filter-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.search-actions {
  justify-content: flex-end;
}

.chips {
  gap: 10px;
  align-items: center;
  margin-top: 6px;
}

.chip {
  cursor: pointer;
}

.chip-active {
  border-color: var(--color-border-dark);
}
</style>
