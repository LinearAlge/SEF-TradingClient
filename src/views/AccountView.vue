<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import FundsSummary from '../components/FundsSummary.vue'
import HoldingsTable from '../components/HoldingsTable.vue'
</script>

<template>
  <AppShell title="Account Overview" subtitle="Cash balance, frozen funds, and holdings">
    <template #actions>
      <button class="btn btn-ghost" type="button">Withdraw</button>
      <button class="btn btn-primary" type="button">Deposit</button>
    </template>

    <section class="grid grid-2">
      <FundsSummary />
      <HoldingsTable />
    </section>
  </AppShell>
</template>
