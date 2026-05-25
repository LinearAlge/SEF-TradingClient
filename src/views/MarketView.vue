<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import StockSearchPanel from '../components/StockSearchPanel.vue'
import MarketTable from '../components/MarketTable.vue'
import PriceTicker from '../components/PriceTicker.vue'
</script>

<template>
<<<<<<< HEAD
  <AppShell title="行情中心" subtitle="最新成交、买一卖一与区间">
    <template #actions>
      <button class="btn btn-primary" type="button">创建提醒</button>
      <button class="btn btn-ghost" type="button">下载行情</button>
=======
  <AppShell title="Market Snapshot" subtitle="Live quotes, best bid, and best ask">
    <template #actions>
      <button class="btn btn-primary" type="button">Create Alert</button>
      <button class="btn btn-ghost" type="button">Download Quotes</button>
>>>>>>> origin/master
    </template>

    <StockSearchPanel />

    <section class="grid grid-2">
      <MarketTable />
      <PriceTicker />
    </section>
  </AppShell>
</template>
