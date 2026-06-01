<script setup lang="ts">
type StockRow = {
  symbol: string
  name: string
  lastPrice: number
  dayHigh: number
  dayLow: number
  bid: number
  ask: number
  volume: number
  changeRate?: number
}

const props = defineProps<{
  stocks: StockRow[]
  loading?: boolean
  error?: string
  asOfLabel?: string
  selectedSymbol?: string
  watchlist?: string[]
}>()

const emit = defineEmits<{
  (event: 'select', symbol: string): void
  (event: 'buy', symbol: string): void
  (event: 'sell', symbol: string): void
  (event: 'alert', symbol: string): void
  (event: 'toggle-watchlist', symbol: string): void
}>()

const isWatchlisted = (symbol: string) => (props.watchlist || []).includes(symbol)

const formatNumber = (value: number) =>
  new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)

const formatVolume = (value: number) => {
  if (value >= 1e8) {
    return `${(value / 1e8).toFixed(2)}亿`
  }
  if (value >= 1e4) {
    return `${(value / 1e4).toFixed(2)}万`
  }
  return value.toString()
}

const formatRate = (value?: number) => {
  if (value === undefined || value === null) return '--'
  return `${(value * 100).toFixed(2)}%`
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <div>
        <div class="card-title">行情看板</div>
        <div class="card-subtitle">买一卖一与价格区间</div>
        <div v-if="asOfLabel" class="sub-meta">{{ asOfLabel }}</div>
      </div>
    </div>
    <div class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>代码</th>
            <th class="numeric">最新价</th>
            <th class="numeric">涨跌幅</th>
            <th class="numeric">最高</th>
            <th class="numeric">最低</th>
            <th class="numeric">买一</th>
            <th class="numeric">卖一</th>
            <th class="numeric">成交量</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="9">加载中...</td>
          </tr>
          <tr v-else-if="error">
            <td colspan="9">{{ error }}</td>
          </tr>
          <tr v-else-if="stocks.length === 0">
            <td colspan="9">暂无行情数据，请输入股票代码或名称查询</td>
          </tr>
          <tr
            v-else
            v-for="item in stocks"
            :key="item.symbol"
            :class="{ 'is-selected': item.symbol === props.selectedSymbol }"
            @click="emit('select', item.symbol)"
          >
            <td>
              <div class="symbol">{{ item.symbol }}</div>
              <div class="name">{{ item.name }}</div>
            </td>
            <td class="numeric">{{ formatNumber(item.lastPrice) }}</td>
            <td class="numeric">{{ formatRate(item.changeRate) }}</td>
            <td class="numeric">{{ formatNumber(item.dayHigh) }}</td>
            <td class="numeric">{{ formatNumber(item.dayLow) }}</td>
            <td class="numeric">{{ formatNumber(item.bid) }}</td>
            <td class="numeric">{{ formatNumber(item.ask) }}</td>
            <td class="numeric">{{ formatVolume(item.volume) }}</td>
            <td>
              <div class="inline-actions">
                <button class="btn btn-small" type="button" @click.stop="emit('buy', item.symbol)">买入</button>
                <button class="btn btn-small" type="button" @click.stop="emit('sell', item.symbol)">卖出</button>
                <button class="btn btn-ghost btn-small" type="button" @click.stop="emit('alert', item.symbol)">提醒</button>
                <button
                  class="btn btn-ghost btn-small"
                  type="button"
                  @click.stop="emit('toggle-watchlist', item.symbol)"
                >
                  {{ isWatchlisted(item.symbol) ? '已自选' : '自选' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.symbol {
  font-weight: 600;
}

.name {
  font-size: 12px;
  color: var(--muted);
}

.sub-meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--muted);
}

tbody tr {
  cursor: pointer;
}

.table-wrap .table {
  min-width: 980px;
}
</style>
