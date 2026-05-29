<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const navGroups = [
  {
    title: '工作台',
    items: [
      { label: '首页', path: '/dashboard' },
      { label: '行情', path: '/market' },
    ],
  },
  {
    title: '交易',
    items: [
      { label: '交易', path: '/trade' },
      { label: '委托成交', path: '/orders' },
    ],
  },
  {
    title: '账户',
    items: [
      { label: '资产', path: '/account' },
      { label: '提醒', path: '/alerts' },
      { label: '安全', path: '/settings' },
    ],
  },
]

const iconMap: Record<string, string> = {
  '/dashboard': '/首页.png',
  '/market': '/行情.png',
  '/trade': '/交易.png',
  '/orders': '/委托成交.png',
  '/account': '/资产.png',
  '/alerts': '/提醒.png',
  '/settings': '/安全.png',
}

const isActive = (path: string) => route.path === path || route.path.startsWith(`${path}/`)

const now = ref(new Date())
let clockTimer: ReturnType<typeof setInterval> | null = null

const formatDate = (date: Date) => {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

const formatTime = (date: Date) =>
  date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  })

const tradingDate = computed(() => formatDate(now.value))
const tradingTime = computed(() => formatTime(now.value))

onMounted(() => {
  clockTimer = setInterval(() => {
    now.value = new Date()
  }, 60000)
})

onUnmounted(() => {
  if (clockTimer) {
    clearInterval(clockTimer)
  }
})
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">
        <img class="brand-icon" src="/favicon.ico" alt="App" />
      </div>
      <div>
        <div class="brand-title">新宇交易</div>
        <div class="brand-subtitle">交易客户端</div>
      </div>
    </div>

    <nav class="nav">
      <div v-for="group in navGroups" :key="group.title" class="nav-group">
        <p class="nav-title">{{ group.title }}</p>
        <RouterLink
          v-for="item in group.items"
          :key="item.path"
          :to="item.path"
          :class="['nav-link', { active: isActive(item.path) }]"
        >
          <img class="nav-icon" :src="iconMap[item.path]" :alt="item.label" />
          {{ item.label }}
        </RouterLink>
      </div>
    </nav>

    <div class="nav-footer card">
      <div class="nav-footer-title">交易日</div>
      <div class="nav-footer-value">{{ tradingDate }}</div>
      <p class="nav-footer-note">当前时间 {{ tradingTime }}</p>
      <p class="nav-footer-note">交易时段 09:30 - 15:00</p>
      <p class="nav-footer-note">行情：正常</p>
      <p class="nav-footer-note">交易通道：正常</p>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  align-self: start;
  min-height: 100vh;
  padding: 28px 22px 32px;
  background: var(--color-bg-aside);
  border-right: 1px solid var(--color-border-light);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 0;
  background: #000000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon {
  width: 26px;
  height: 26px;
  object-fit: contain;
}

.brand-title {
  font-weight: 700;
  font-size: 18px;
}

.brand-subtitle {
  font-size: 12px;
  color: var(--muted);
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.nav-title {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 11px;
  color: var(--muted);
  margin: 0 0 10px;
}

.nav-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 0;
  font-weight: 600;
  color: var(--ink);
  background: transparent;
  transition: background 0.2s ease, transform 0.2s ease;
}

.nav-link:hover {
  background: var(--color-bg-main);
  transform: translateX(2px);
}

.nav-link.active {
  background: var(--color-border);
  color: var(--color-text-primary);
}

.nav-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.nav-footer {
  margin-top: auto;
  padding: 16px;
}

.nav-footer-title {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.nav-footer-value {
  font-size: 18px;
  font-weight: 600;
  margin-top: 8px;
}

.nav-footer-note {
  font-size: 12px;
  color: var(--muted);
  margin: 6px 0 0;
}

@media (max-width: 960px) {
  .sidebar {
    position: relative;
    min-height: auto;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }
}
</style>
