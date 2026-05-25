<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  mode: 'buy' | 'sell'
}>()

<<<<<<< HEAD
const heading = computed(() => (props.mode === 'buy' ? '买入委托' : '卖出委托'))
const chipLabel = computed(() => (props.mode === 'buy' ? '资金' : '持仓'))
=======
const heading = computed(() => (props.mode === 'buy' ? 'Buy Order' : 'Sell Order'))
const chipLabel = computed(() => (props.mode === 'buy' ? 'Funds' : 'Holdings'))
>>>>>>> origin/master
</script>

<template>
  <div class="card trade-ticket">
    <div class="ticket-header">
      <div>
        <div class="card-title">{{ heading }}</div>
<<<<<<< HEAD
        <div class="card-subtitle">提交到撮合系统</div>
=======
        <div class="card-subtitle">Route to the central matching system</div>
>>>>>>> origin/master
      </div>
      <div class="chip">{{ chipLabel }} linked</div>
    </div>

    <form class="ticket-form">
      <label class="field">
<<<<<<< HEAD
        股票代码
        <input class="input" placeholder="例如 QST" />
      </label>
      <label class="field">
        委托类型
        <select class="select">
          <option>限价</option>
          <option>市价</option>
          <option>止损</option>
        </select>
      </label>
      <label class="field">
        价格
        <input class="input" placeholder="112.40" />
      </label>
      <label class="field">
        数量
        <input class="input" placeholder="100" />
      </label>
      <label class="field">
        有效期
        <select class="select">
          <option>当日有效</option>
          <option>撤销前有效</option>
        </select>
      </label>
      <label class="field">
        备注
        <textarea class="textarea" rows="3" placeholder="可选备注"></textarea>
      </label>
      <div class="ticket-actions">
        <button class="btn btn-ghost" type="button">预览</button>
        <button class="btn btn-primary" type="button">提交委托</button>
=======
        Symbol
        <input class="input" placeholder="e.g. QST" />
      </label>
      <label class="field">
        Order Type
        <select class="select">
          <option>Limit</option>
          <option>Market</option>
          <option>Stop</option>
        </select>
      </label>
      <label class="field">
        Price
        <input class="input" placeholder="112.40" />
      </label>
      <label class="field">
        Quantity
        <input class="input" placeholder="100" />
      </label>
      <label class="field">
        Validity
        <select class="select">
          <option>Day</option>
          <option>Good till canceled</option>
        </select>
      </label>
      <label class="field">
        Notes
        <textarea class="textarea" rows="3" placeholder="Optional instruction"></textarea>
      </label>
      <div class="ticket-actions">
        <button class="btn btn-ghost" type="button">Preview</button>
        <button class="btn btn-primary" type="button">Submit Order</button>
>>>>>>> origin/master
      </div>
    </form>
  </div>
</template>

<style scoped>
.trade-ticket {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.ticket-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.ticket-form {
  display: grid;
  gap: 14px;
}

.ticket-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  flex-wrap: wrap;
}
</style>
