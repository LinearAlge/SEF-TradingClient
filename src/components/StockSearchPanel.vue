<script setup lang="ts">
const filters = [
  { label: 'Today', active: true },
  { label: 'Week', active: false },
  { label: 'Month', active: false },
  { label: 'Quarter', active: false },
]
</script>

<template>
  <div class="card search-panel">
    <div>
      <div class="card-title">Stock Lookup</div>
      <div class="card-subtitle">Find price bands, best bid, and best ask</div>
    </div>
    <div class="search-grid">
      <label class="field">
        Symbol or Name
        <input class="input" placeholder="Search QST or Quartz" />
      </label>
      <label class="field">
        Exchange
        <select class="select">
          <option>Main Board</option>
          <option>Growth</option>
          <option>ST Board</option>
        </select>
      </label>
      <label class="field">
        Quote Refresh
        <select class="select">
          <option>5 seconds</option>
          <option>15 seconds</option>
          <option>30 seconds</option>
        </select>
      </label>
      <div class="field">
        Range
        <div class="filter-row">
          <button
            v-for="item in filters"
            :key="item.label"
            class="btn"
            type="button"
            :class="item.active ? 'btn-primary' : ''"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>
    <div class="search-actions">
      <button class="btn btn-ghost" type="button">Reset</button>
      <button class="btn btn-primary" type="button">Run Query</button>
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
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.filter-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.search-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
