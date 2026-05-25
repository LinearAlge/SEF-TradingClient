<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import OrderListTable from '../components/OrderListTable.vue'
</script>

<template>
<<<<<<< HEAD
  <AppShell title="委托管理" subtitle="跟踪状态、撤单与成交回报">
    <template #actions>
      <button class="btn btn-ghost" type="button">批量撤单</button>
      <button class="btn btn-primary" type="button">导出委托</button>
    </template>

    <div class="order-filters">
      <span class="chip">全部</span>
      <span class="chip">未成交</span>
      <span class="chip">部分成交</span>
      <span class="chip">已成交</span>
      <span class="chip">已撤单</span>
    </div>

    <OrderListTable title="全部委托" subtitle="近 30 日记录" />
=======
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
>>>>>>> origin/master
  </AppShell>
</template>

<style scoped>
.order-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
