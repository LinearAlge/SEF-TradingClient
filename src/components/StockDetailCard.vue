<script setup lang="ts">
import { useRouter } from 'vue-router'

type StockDetail = {
  symbol: string
  name: string
  board: string
  lastPrice: number
  bid: number
  ask: number
  dayHigh: number
  dayLow: number
  weekHigh: number
  weekLow: number
  monthHigh: number
  monthLow: number
  volume: number
  announcements: string[]
}

const props = defineProps<{
  stock: StockDetail | null
  loading?: boolean
  error?: string
  asOfLabel?: string
}>()

const router = useRouter()

const goTrade = (side: 'buy' | 'sell') => {
  if (!props.stock) return
  router.push({ path: '/trade', query: { symbol: props.stock.symbol, side } })
}

const goAlert = () => {
  if (!props.stock) return
  router.push({ path: '/alerts', query: { symbol: props.stock.symbol } })
}

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

const calcLimit = (value?: number, ratio = 1.1) => {
  if (!value) return '--'
  return formatNumber(value * ratio)
}
</script>

<template>
	<div class="card">
    <div class="card-title">股票详情</div>
    <div class="card-subtitle">关键价格区间与公告</div>
    <div v-if="asOfLabel" class="sub-meta">{{ asOfLabel }}</div>

    <div v-if="loading" class="empty">加载中...</div>
    <div v-else-if="error" class="empty">{{ error }}</div>
    <div v-else-if="!stock" class="empty">请选择一只股票查看详情</div>
    <div v-else class="detail-grid">
      <div class="detail-item">
        <div class="detail-label">股票</div>
        <div class="detail-value">{{ stock.symbol }} · {{ stock.name }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">板块</div>
        <div class="detail-value">{{ stock.board }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">最新价</div>
        <div class="detail-value">{{ formatNumber(stock.lastPrice) }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">买一 / 卖一</div>
        <div class="detail-value">
          {{ formatNumber(stock.bid) }} / {{ formatNumber(stock.ask) }}
        </div>
      </div>
      <div class="detail-item">
        <div class="detail-label">当日最高/最低</div>
        <div class="detail-value">
          {{ formatNumber(stock.dayHigh) }} / {{ formatNumber(stock.dayLow) }}
        </div>
      </div>
      <div class="detail-item">
        <div class="detail-label">本周最高/最低</div>
        <div class="detail-value">
          {{ formatNumber(stock.weekHigh) }} / {{ formatNumber(stock.weekLow) }}
        </div>
      </div>
      <div class="detail-item">
        <div class="detail-label">本月最高/最低</div>
        <div class="detail-value">
          {{ formatNumber(stock.monthHigh) }} / {{ formatNumber(stock.monthLow) }}
        </div>
      </div>
      <div class="detail-item">
        <div class="detail-label">成交量</div>
        <div class="detail-value">{{ formatVolume(stock.volume) }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">价格边界</div>
        <div class="detail-value">
          涨停 {{ calcLimit(stock.lastPrice, 1.1) }} / 跌停 {{ calcLimit(stock.lastPrice, 0.9) }}
        </div>
      </div>
      <div class="detail-item">
        <div class="detail-label">快捷操作</div>
        <div class="inline-actions">
          <button class="btn btn-small" type="button" @click="goTrade('buy')">买入</button>
          <button class="btn btn-small" type="button" @click="goTrade('sell')">卖出</button>
          <button class="btn btn-ghost btn-small" type="button" @click="goAlert">设置提醒</button>
        </div>
      </div>
      <div class="detail-item">
        <div class="detail-label">简化盘口</div>
        <div class="orderbook">
          <div>
            <span class="orderbook-label">买一</span>
            <span class="orderbook-value">{{ formatNumber(stock.bid) }}</span>
          </div>
          <div>
            <span class="orderbook-label">卖一</span>
            <span class="orderbook-value">{{ formatNumber(stock.ask) }}</span>
          </div>
        </div>
      </div>
      <div class="detail-item full">
        <div class="detail-label">重要公告</div>
        <ul class="announcements">
          <li v-for="item in stock.announcements" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.detail-item {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  background: #ffffff;
}

.detail-item.full {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.detail-value {
  margin-top: 6px;
  font-size: 16px;
  font-weight: 600;
}

.orderbook {
  display: grid;
  gap: 6px;
  margin-top: 6px;
  font-size: 13px;
}

.orderbook-label {
  color: var(--muted);
  margin-right: 8px;
}

.orderbook-value {
  font-weight: 600;
}

.announcements {
  margin: 8px 0 0;
  padding-left: 16px;
  color: var(--muted);
  font-size: 13px;
}

.empty {
  margin-top: 12px;
  font-size: 13px;
  color: var(--muted);
}

.sub-meta {
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--muted);
}
</style>
