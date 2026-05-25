<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
import StatCard from '../components/StatCard.vue'
import HoldingsTable from '../components/HoldingsTable.vue'
import OrderListTable from '../components/OrderListTable.vue'
import PriceTicker from '../components/PriceTicker.vue'
</script>

<template>
  <AppShell title="交易总览" subtitle="资金、持仓与委托概览">
    <template #actions>
      <button class="btn btn-primary" type="button">新建委托</button>
      <button class="btn btn-ghost" type="button">导出</button>
    </template>

    <section class="grid grid-3">
      <StatCard
        title="可用资金"
        value="$128,420"
        change="+4.2%"
        note="较上一交易日"
        tone="positive"
      />
      <StatCard
        title="冻结资金"
        value="$18,600"
        change="-1.3%"
        note="未成交委托占用"
        tone="negative"
      />
      <StatCard
        title="资产总值"
        value="$412,890"
        change="+1.1%"
        note="当日资产合计"
        tone="positive"
      />
    </section>

    <section class="grid grid-2">
      <HoldingsTable />
      <div class="grid">
        <PriceTicker />
        <OrderListTable title="最新委托" subtitle="本席位最新委托" />
      </div>
    </section>
  </AppShell>
</template>
