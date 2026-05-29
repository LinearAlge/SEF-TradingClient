<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const props = withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    showSearch?: boolean
    searchPlaceholder?: string
    showRefresh?: boolean
    refreshLabel?: string
    refreshing?: boolean
    lastUpdated?: string
    statusItems?: { label: string; value: string }[]
    onRefresh?: () => void
    onSearch?: (value: string) => void
  }>(),
  {
    showSearch: false,
    searchPlaceholder: '搜索股票代码、名称或委托号',
    showRefresh: false,
    refreshLabel: '刷新',
    refreshing: false,
  },
)

const accountId = computed(() => localStorage.getItem('trading-account') || 'admin')
const searchText = ref('')
const router = useRouter()

const resolvedStatusItems = computed(() =>
  props.statusItems && props.statusItems.length > 0
    ? props.statusItems
    : [
        { label: '当前资金账号', value: accountId.value },
        { label: '行情连接', value: '正常' },
        { label: '交易通道', value: '正常' },
      ],
)

const handleSearch = () => {
  if (!searchText.value.trim()) return
  if (props.onSearch) {
    props.onSearch(searchText.value.trim())
    return
  }
  router.push({ path: '/market', query: { q: searchText.value.trim() } })
}

const handleRefresh = () => {
  props.onRefresh?.()
}
</script>

<template>
  <header class="topbar">
    <div class="title-block">
      <h1 class="title">{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <div class="tools">
      <div v-if="showSearch" class="search">
        <input
          v-model="searchText"
          class="input"
          :placeholder="searchPlaceholder"
          @keyup.enter="handleSearch"
        />
      </div>
      <button
        v-if="showRefresh"
        class="btn btn-ghost"
        type="button"
        :disabled="refreshing"
        @click="handleRefresh"
      >
        {{ refreshing ? '刷新中...' : refreshLabel }}
      </button>
      <div class="actions">
        <slot name="actions" />
      </div>
    </div>
  </header>
  <div class="topbar-meta">
    <div v-for="item in resolvedStatusItems" :key="item.label" class="meta-item">
      <span class="meta-label">{{ item.label }}</span>
      <span class="meta-value">{{ item.value }}</span>
    </div>
    <div v-if="lastUpdated" class="meta-item">
      <span class="meta-label">更新时间</span>
      <span class="meta-value">{{ lastUpdated }}</span>
    </div>
  </div>
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
  font-size: 22px;
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

.topbar-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--muted);
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 10px;
}

.meta-value {
  font-weight: 600;
  color: var(--ink);
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
