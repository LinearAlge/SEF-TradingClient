<script setup lang="ts">
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
    title: '资产',
    items: [
      { label: '资产', path: '/account' },
      { label: '提醒', path: '/alerts' },
      { label: '安全', path: '/settings' },
    ],
  },
]

const isActive = (path: string) => route.path === path || route.path.startsWith(`${path}/`)
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark"></div>
      <div>
        <div class="brand-title">栖木交易</div>
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
          <span class="nav-indicator"></span>
          {{ item.label }}
        </RouterLink>
      </div>
    </nav>

    <div class="nav-footer card">
      <div class="nav-footer-title">交易日</div>
      <div class="nav-footer-value">2026-05-25</div>
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

.nav-indicator {
  width: 8px;
  height: 8px;
  border-radius: 0;
  background: var(--accent);
  opacity: 0.6;
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
