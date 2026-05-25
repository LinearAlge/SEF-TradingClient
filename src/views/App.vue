<script setup lang="ts"></script>

<template>
  <div class="app-root">
    <RouterView />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

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
  border: 1px solid rgba(0, 0, 0, 0.03);
  border-radius: 0;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.015), 0 2px 8px -1px rgba(0, 0, 0, 0.01);
  padding: 20px 22px;
  animation: appleCardRise 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 6px;
}

.card-subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0 0 14px;
}

.btn {
  border: 1px solid var(--color-border);
  background: #ffffff;
  color: var(--color-text-primary);
  padding: 10px 16px;
  border-radius: 0;
  font-weight: 600;
  font-size: 14px;
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
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.grid-3 {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.table thead tr {
  border-top: 2px solid var(--color-border-dark);
  border-bottom: 1px solid var(--color-border-dark);
}

.table th,
.table td {
  text-align: left;
  padding: 10px 6px;
  border-bottom: 1px solid #f3f4f6;
}

.table th {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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

@media (max-width: 900px) {
  .page {
    padding: 24px 20px 60px;
  }
}
</style>
