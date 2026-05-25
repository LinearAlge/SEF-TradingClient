<script setup lang="ts">
const filters = [
  { label: '今日', active: true },
  { label: '本周', active: false },
  { label: '本月', active: false },
  { label: '本季', active: false },
]
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
        <input class="input" placeholder="例如 QST 或 石英" />
      </label>
      <label class="field">
        交易板块
        <select class="select">
          <option>主板</option>
          <option>创业板</option>
          <option>ST 板</option>
        </select>
      </label>
      <label class="field">
        行情刷新
        <select class="select">
          <option>5 秒</option>
          <option>15 秒</option>
          <option>30 秒</option>
        </select>
      </label>
      <div class="field">
        区间
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
      <button class="btn btn-ghost" type="button">重置</button>
      <button class="btn btn-primary" type="button">查询</button>
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
