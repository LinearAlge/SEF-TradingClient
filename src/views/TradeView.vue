<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import TradeTicket from '../components/TradeTicket.vue'
import OrderListTable from '../components/OrderListTable.vue'
</script>

<template>
  <AppShell title="下单台" subtitle="提交买卖委托到撮合系统">
    <template #actions>
      <button class="btn btn-ghost" type="button">全部撤单</button>
      <button class="btn btn-primary" type="button">查看限价</button>
    </template>

    <section class="grid grid-2">
      <TradeTicket mode="buy" />
      <TradeTicket mode="sell" />
    </section>

    <OrderListTable title="当前委托" subtitle="待撮合的委托" />
  </AppShell>
</template>
