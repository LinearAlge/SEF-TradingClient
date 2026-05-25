<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import AlertsList from '../components/AlertsList.vue'
import PriceTicker from '../components/PriceTicker.vue'
</script>

<template>
  <AppShell title="提醒管理" subtitle="价格触发提醒">
    <template #actions>
      <button class="btn btn-primary" type="button">新增提醒</button>
      <button class="btn btn-ghost" type="button">全部暂停</button>
    </template>

    <section class="grid grid-2">
      <AlertsList />
      <PriceTicker />
    </section>
  </AppShell>
</template>
