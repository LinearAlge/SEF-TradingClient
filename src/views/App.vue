<script setup lang="ts"></script>

<template>
  <div class="app-root">
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-grid"></div>
    <RouterView />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  color-scheme: light;
  font-family: 'Space Grotesk', 'IBM Plex Sans', 'Segoe UI', sans-serif;
  --bg: #f6f1e9;
  --bg-alt: #fff6e9;
  --panel: #fffaf3;
  --ink: #1f2623;
  --muted: #5e6b60;
  --primary: #1f7a5d;
  --primary-ink: #0f3d2d;
  --accent: #f4a261;
  --accent-ink: #7b3a06;
  --border: #e3d6c6;
  --shadow: 0 24px 60px rgba(31, 38, 35, 0.12);
  --radius-lg: 24px;
  --radius-md: 16px;
  --radius-sm: 10px;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  letter-spacing: 0.1px;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  font-family: inherit;
}

.app-root {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding-bottom: 60px;
}

.bg-orb {
  position: fixed;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  filter: blur(0px);
  opacity: 0.6;
  pointer-events: none;
  z-index: 0;
}

.orb-1 {
  top: -120px;
  left: -120px;
  background: radial-gradient(circle at 30% 30%, #ffd3a5, transparent 70%);
}

.orb-2 {
  bottom: -140px;
  right: -140px;
  background: radial-gradient(circle at 70% 40%, #b8f2dc, transparent 65%);
}

.bg-grid {
  position: fixed;
  inset: 0;
  background-image: linear-gradient(to right, rgba(31, 38, 35, 0.04) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(31, 38, 35, 0.04) 1px, transparent 1px);
  background-size: 80px 80px;
  pointer-events: none;
  z-index: 0;
  opacity: 0.5;
}

.page {
  position: relative;
  z-index: 1;
  padding: 32px 40px 64px;
}

.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 20px 22px;
  animation: rise 0.6s ease both;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 6px;
}

.card-subtitle {
  font-size: 13px;
  color: var(--muted);
  margin: 0 0 14px;
}

.btn {
  border: 1px solid var(--border);
  background: transparent;
  color: var(--ink);
  padding: 10px 16px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(31, 38, 35, 0.12);
}

.btn-primary {
  background: var(--primary);
  color: #f5fff9;
  border-color: transparent;
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.6);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(31, 122, 93, 0.12);
  color: var(--primary-ink);
  font-size: 12px;
  font-weight: 600;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--muted);
}

.input,
.select,
.textarea {
  border: 1px solid var(--border);
  background: #fffdf7;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--ink);
}

.input:focus,
.select:focus,
.textarea:focus {
  outline: 2px solid rgba(31, 122, 93, 0.2);
  border-color: rgba(31, 122, 93, 0.6);
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

.table th,
.table td {
  text-align: left;
  padding: 10px 6px;
  border-bottom: 1px solid var(--border);
}

.table th {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}

.tag-positive {
  color: #1b7f5d;
  font-weight: 600;
}

.tag-negative {
  color: #b4552d;
  font-weight: 600;
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .page {
    padding: 24px 20px 60px;
  }
}
</style>
