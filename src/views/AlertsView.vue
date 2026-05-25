<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import AlertsList from '../components/AlertsList.vue'
import PriceTicker from '../components/PriceTicker.vue'
</script>

<template>
  <AppShell title="Alerts" subtitle="Optional reminders for price movement">
    <template #actions>
      <button class="btn btn-primary" type="button">New Alert</button>
      <button class="btn btn-ghost" type="button">Pause All</button>
    </template>

    <section class="grid grid-2">
      <AlertsList />
      <PriceTicker />
    </section>
  </AppShell>
</template>
