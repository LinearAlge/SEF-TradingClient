<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import TradeTicket from '../components/TradeTicket.vue'
import OrderListTable from '../components/OrderListTable.vue'
</script>

<template>
  <AppShell title="Trade Desk" subtitle="Send buy and sell orders to the matching engine">
    <template #actions>
      <button class="btn btn-ghost" type="button">Cancel All</button>
      <button class="btn btn-primary" type="button">Review Limits</button>
    </template>

    <section class="grid grid-2">
      <TradeTicket mode="buy" />
      <TradeTicket mode="sell" />
    </section>

    <OrderListTable title="Open Orders" subtitle="Active orders awaiting match" />
  </AppShell>
</template>
