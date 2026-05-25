<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const navGroups = [
  {
    title: 'Overview',
    items: [
      { label: 'Dashboard', path: '/dashboard' },
      { label: 'Market', path: '/market' },
    ],
  },
  {
    title: 'Trading',
    items: [
      { label: 'Trade Ticket', path: '/trade' },
      { label: 'Orders', path: '/orders' },
    ],
  },
  {
    title: 'Account',
    items: [
      { label: 'Account', path: '/account' },
      { label: 'Alerts', path: '/alerts' },
      { label: 'Settings', path: '/settings' },
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
        <div class="brand-title">Arbor Trade</div>
        <div class="brand-subtitle">Client Console</div>
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
      <div class="nav-footer-title">Trading Day</div>
      <div class="nav-footer-value">May 25, 2026</div>
      <p class="nav-footer-note">Session open 09:30 - 15:00</p>
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
  background: rgba(255, 250, 243, 0.92);
  border-right: 1px solid var(--border);
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
  border-radius: 14px;
  background: conic-gradient(from 210deg, #1f7a5d, #f4a261, #1f7a5d);
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
  border-radius: 12px;
  font-weight: 600;
  color: var(--ink);
  background: transparent;
  transition: background 0.2s ease, transform 0.2s ease;
}

.nav-link:hover {
  background: rgba(31, 122, 93, 0.08);
  transform: translateX(2px);
}

.nav-link.active {
  background: rgba(31, 122, 93, 0.16);
  color: var(--primary-ink);
}

.nav-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
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
