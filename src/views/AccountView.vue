<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import FundsSummary from '../components/FundsSummary.vue'
import HoldingsTable from '../components/HoldingsTable.vue'
</script>

<template>
  <AppShell title="账户概览" subtitle="资金余额、冻结资金与持仓">
    <template #actions>
      <button class="btn btn-ghost" type="button">取款</button>
      <button class="btn btn-primary" type="button">存款</button>
    </template>

    <section class="grid grid-2">
      <FundsSummary />
      <HoldingsTable />
    </section>
  </AppShell>
</template>
