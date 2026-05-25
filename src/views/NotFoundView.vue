<template>
  <div class="not-found">
    <div class="card">
      <h1>Page not found</h1>
      <p class="card-subtitle">The page you are looking for does not exist.</p>
      <RouterLink class="btn btn-primary" to="/dashboard">Back to dashboard</RouterLink>
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
