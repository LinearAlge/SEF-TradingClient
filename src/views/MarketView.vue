<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import StockSearchPanel from '../components/StockSearchPanel.vue'
import MarketTable from '../components/MarketTable.vue'
import PriceTicker from '../components/PriceTicker.vue'
</script>

<template>
  <AppShell title="Market Snapshot" subtitle="Live quotes, best bid, and best ask">
    <template #actions>
      <button class="btn btn-primary" type="button">Create Alert</button>
      <button class="btn btn-ghost" type="button">Download Quotes</button>
    </template>

    <StockSearchPanel />

    <section class="grid grid-2">
      <MarketTable />
      <PriceTicker />
    </section>
  </AppShell>
</template>
