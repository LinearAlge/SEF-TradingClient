<script setup lang="ts"></script>

<template>
  <div class="app-root">
    <RouterView />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  color-scheme: light;
  --ink: var(--color-text-primary);
  --muted: var(--color-text-muted);
  --border: var(--color-border);
  --accent: #000000;
  --primary-ink: var(--color-text-primary);
  --accent-positive: #15803d;
  --accent-negative: #b91c1c;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--color-bg-main);
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  font-family: inherit;
}

.app-root {
  min-height: 100vh;
  padding-bottom: 40px;
  background: var(--color-bg-main);
}

.page {
  padding: 40px;
}

.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 0;
  box-shadow: none;
  padding: 14px 16px;
  min-width: 0;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 6px;
}

.card-subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0 0 10px;
}

.panel {
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  padding: 14px 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 10px;
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  margin: 0;
}

.panel-subtitle {
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 4px 0 0;
}

.btn {
  border: 1px solid var(--color-border);
  background: #ffffff;
  color: var(--color-text-primary);
  padding: 8px 14px;
  border-radius: 0;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out, color 0.15s ease-in-out,
    border-color 0.15s ease-in-out;
}

.btn-primary {
  background: #000000;
  color: #ffffff;
  border: 1px solid #000000;
}

.btn-primary:hover {
  background: #1f2937;
  border-color: #1f2937;
}

.btn-ghost {
  background: #ffffff;
  color: #000000;
  border: 2px solid #000000;
}

.btn-ghost:hover {
  background: #000000;
  color: #ffffff;
  border-color: #000000;
}

.btn-danger {
  background: #ffffff;
  border: 1px solid #b91c1c;
  color: #b91c1c;
}

.btn-danger:hover {
  background: #b91c1c;
  color: #ffffff;
}

.btn-small {
  padding: 6px 10px;
  font-size: 12px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 0;
  border: 1px solid var(--color-border-dark);
  background: #ffffff;
  color: var(--color-text-primary);
  font-size: 12px;
  font-weight: 600;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.input,
.select,
.textarea {
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  padding: 10px 12px;
  border-radius: 0;
  font-size: 14px;
  color: var(--color-text-primary);
}

.input:focus,
.select:focus,
.textarea:focus {
  outline: none;
  border-color: var(--color-border-dark);
  box-shadow: 0 0 0 1px var(--color-border-dark);
}

.grid {
  display: grid;
  gap: 20px;
}

.grid-2 {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.grid-3 {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
}

.table-wrap .table {
  min-width: 860px;
}

.table thead tr {
  border-top: 2px solid var(--color-border-dark);
  border-bottom: 1px solid var(--color-border-dark);
}

.table th,
.table td {
  text-align: left;
  padding: 10px 8px;
  border-bottom: 1px solid #eef0f2;
}

.table th {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.table tbody tr:hover {
  background: #f8f9fb;
}

.table tbody tr.is-selected {
  background: #f3f4f6;
  box-shadow: inset 3px 0 0 #000000;
}

.numeric {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 0;
  border: 1px solid var(--color-border);
  font-size: 12px;
  font-weight: 600;
}

.status-pill.positive {
  color: var(--accent-positive);
  border-color: rgba(21, 128, 61, 0.3);
}

.status-pill.negative {
  color: var(--accent-negative);
  border-color: rgba(185, 28, 28, 0.3);
}

.status-pill.neutral {
  color: var(--color-text-muted);
}

.tag-positive {
  color: var(--accent-positive);
  font-weight: 600;
}

.tag-negative {
  color: var(--accent-negative);
  font-weight: 600;
}

.metric-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.metric-strip .metric {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  padding: 12px 14px;
}

.metric-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-text-muted);
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  margin-top: 6px;
}

.metric-note {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 4px;
}

.meta-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--color-text-muted);
}

.inline-actions {
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.empty-state {
  padding: 16px;
  border: 1px dashed var(--color-border);
  color: var(--color-text-muted);
  font-size: 13px;
}

.form-hint {
  font-size: 12px;
  color: var(--color-text-muted);
}

.price-up {
  color: var(--accent-positive);
}

.price-down {
  color: var(--accent-negative);
}

.price-flat {
  color: var(--color-text-muted);
}

.layout-split {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
  gap: 20px;
}

@media (max-width: 900px) {
  .page {
    padding: 24px 20px 60px;
  }

  .layout-split {
    grid-template-columns: 1fr;
  }
}
</style>
