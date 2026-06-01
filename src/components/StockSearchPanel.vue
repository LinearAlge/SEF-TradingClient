<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['search', 'reset'])

const query = ref('')
const board = ref('主板')

const handleSearch = () => {
  emit('search', {
    query: query.value.trim(),
    board: board.value,
  })
}

const handleReset = () => {
  query.value = ''
  board.value = '主板'
  emit('reset')
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

.search-actions {
  justify-content: flex-end;
}
</style>
