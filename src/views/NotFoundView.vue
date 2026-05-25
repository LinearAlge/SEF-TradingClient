<template>
  <div class="not-found">
    <div class="card">
      <h1>页面不存在</h1>
      <p class="card-subtitle">你访问的页面不存在。</p>
      <RouterLink class="btn btn-primary" to="/dashboard">返回总览</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

h1 {
  margin: 0 0 8px;
}
</style>
