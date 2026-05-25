<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import OrderListTable from '../components/OrderListTable.vue'
</script>

<template>
  <AppShell title="Orders" subtitle="Track status, cancel, or review executions">
    <template #actions>
      <button class="btn btn-ghost" type="button">Cancel Selected</button>
      <button class="btn btn-primary" type="button">Export Orders</button>
    </template>

    <div class="order-filters">
      <span class="chip">All</span>
      <span class="chip">Open</span>
      <span class="chip">Partial</span>
      <span class="chip">Filled</span>
      <span class="chip">Canceled</span>
    </div>

    <OrderListTable title="All Orders" subtitle="Last 30 days of activity" />
  </AppShell>
</template>

<style scoped>
.order-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
