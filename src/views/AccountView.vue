<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import FundsSummary from '../components/FundsSummary.vue'
import HoldingsTable from '../components/HoldingsTable.vue'
import { addCashFlow, addStockFlow, loadCashFlows, loadStockFlows } from '../utils/tradingLocalStore'

const cashFlows = ref(loadCashFlows())
const stockFlows = ref(loadStockFlows())
const refreshKey = ref(0)

const seedFlows = () => {
  if (cashFlows.value.length === 0) {
    cashFlows.value = addCashFlow({
      id: 'CASH-01',
      time: '10:02',
      type: '买入冻结',
      amount: '-23,840.00',
      status: '已完成',
    })
  }
  if (stockFlows.value.length === 0) {
    stockFlows.value = addStockFlow({
      id: 'STK-01',
      time: '10:10',
      type: '卖出成交',
      symbol: '600002',
      qty: '-80',
      status: '已完成',
    })
  }
}

const refreshFlows = () => {
  cashFlows.value = loadCashFlows()
  stockFlows.value = loadStockFlows()
  seedFlows()
  refreshKey.value += 1
}

onMounted(() => {
  seedFlows()
})
</script>

<template>
  <AppShell
    title="资产"
    subtitle="资金余额、冻结资金与持仓"
    :showSearch="false"
    :showRefresh="true"
    refreshLabel="刷新资产"
    :onRefresh="refreshFlows"
  >
    <template #actions>
      <button class="btn btn-ghost" type="button">取款</button>
      <button class="btn btn-primary" type="button">存款</button>
    </template>

    <section class="grid grid-2">
      <FundsSummary :refreshKey="refreshKey" />
      <HoldingsTable :refreshKey="refreshKey" />
    </section>

    <section class="grid grid-2">
      <div class="card">
        <div class="card-title">资金流水</div>
        <div class="card-subtitle">买入冻结、撤单解冻与资金入账</div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>时间</th>
                <th>类型</th>
                <th class="numeric">金额</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in cashFlows" :key="item.id">
                <td>{{ item.time }}</td>
                <td>{{ item.type }}</td>
                <td class="numeric">{{ item.amount }}</td>
                <td><span class="status-pill positive">{{ item.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <div class="card-title">证券流水</div>
        <div class="card-subtitle">成交入股与卖出出股</div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>时间</th>
                <th>类型</th>
                <th>股票</th>
                <th class="numeric">数量</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in stockFlows" :key="item.id">
                <td>{{ item.time }}</td>
                <td>{{ item.type }}</td>
                <td>{{ item.symbol }}</td>
                <td class="numeric">{{ item.qty }}</td>
                <td><span class="status-pill positive">{{ item.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </AppShell>
</template>
