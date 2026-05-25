<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import StatCard from '../components/StatCard.vue'
import HoldingsTable from '../components/HoldingsTable.vue'
import OrderListTable from '../components/OrderListTable.vue'
import PriceTicker from '../components/PriceTicker.vue'
</script>

<template>
  <AppShell title="Trading Dashboard" subtitle="Overview of funds, holdings, and live orders">
    <template #actions>
      <button class="btn btn-primary" type="button">New Order</button>
      <button class="btn btn-ghost" type="button">Export</button>
    </template>

    <section class="grid grid-3">
      <StatCard
        title="Available Cash"
        value="$128,420"
        change="+4.2%"
        note="Compared with last session"
        tone="positive"
      />
      <StatCard
        title="Frozen Funds"
        value="$18,600"
        change="-1.3%"
        note="Open orders reserved"
        tone="negative"
      />
      <StatCard
        title="Portfolio Value"
        value="$412,890"
        change="+1.1%"
        note="Total equity today"
        tone="positive"
      />
    </section>

    <section class="grid grid-2">
      <HoldingsTable />
      <div class="grid">
        <PriceTicker />
        <OrderListTable title="Latest Orders" subtitle="Most recent requests from your desk" />
      </div>
    </section>
  </AppShell>
</template>
