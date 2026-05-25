<script setup lang="ts">
import SidebarNav from './SidebarNav.vue'
import TopBar from './TopBar.vue'

defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <div class="shell">
    <SidebarNav />
    <div class="shell-main">
      <TopBar :title="title" :subtitle="subtitle">
        <template #actions>
          <slot name="actions" />
        </template>
      </TopBar>
      <main class="shell-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.shell {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

.shell-main {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 28px 32px 40px;
}

.shell-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@media (max-width: 960px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .shell-main {
    padding: 20px;
  }
}
</style>
