<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <header class="topbar">
    <div class="title-block">
      <h1 class="title">{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <div class="tools">
      <div class="search">
        <input class="input" placeholder="Search ticker, account, or order" />
      </div>
      <div class="actions">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.title-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.title {
  font-size: 28px;
  margin: 0;
}

.subtitle {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.tools {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search {
  min-width: 240px;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

@media (max-width: 720px) {
  .search {
    width: 100%;
  }
}
</style>
