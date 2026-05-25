<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import TradeTicket from '../components/TradeTicket.vue'
import OrderListTable from '../components/OrderListTable.vue'
</script>

<template>
<<<<<<< HEAD
  <AppShell title="下单台" subtitle="提交买卖委托到撮合系统">
    <template #actions>
      <button class="btn btn-ghost" type="button">全部撤单</button>
      <button class="btn btn-primary" type="button">查看限价</button>
=======
  <AppShell title="Trade Desk" subtitle="Send buy and sell orders to the matching engine">
    <template #actions>
      <button class="btn btn-ghost" type="button">Cancel All</button>
      <button class="btn btn-primary" type="button">Review Limits</button>
>>>>>>> origin/master
    </template>

    <section class="grid grid-2">
      <TradeTicket mode="buy" />
      <TradeTicket mode="sell" />
    </section>

<<<<<<< HEAD
    <OrderListTable title="当前委托" subtitle="待撮合的委托" />
=======
    <OrderListTable title="Open Orders" subtitle="Active orders awaiting match" />
>>>>>>> origin/master
  </AppShell>
</template>
