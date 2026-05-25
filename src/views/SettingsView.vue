<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
</script>

<template>
  <AppShell title="Security Settings" subtitle="Update trading and withdrawal passwords">
    <template #actions>
      <button class="btn btn-ghost" type="button">Verify Certificate</button>
      <button class="btn btn-primary" type="button">Save Changes</button>
    </template>

    <section class="grid grid-2">
      <div class="card">
        <div class="card-title">Trading Password</div>
        <div class="card-subtitle">Required for buy and sell orders</div>
        <form class="form-grid">
          <label class="field">
            Current Password
            <input class="input" type="password" placeholder="Enter current password" />
          </label>
          <label class="field">
            New Password
            <input class="input" type="password" placeholder="Enter new password" />
          </label>
          <label class="field">
            Confirm Password
            <input class="input" type="password" placeholder="Confirm new password" />
          </label>
        </form>
      </div>
      <div class="card">
        <div class="card-title">Withdrawal Password</div>
        <div class="card-subtitle">Required for cash withdrawal</div>
        <form class="form-grid">
          <label class="field">
            Current Password
            <input class="input" type="password" placeholder="Enter current password" />
          </label>
          <label class="field">
            New Password
            <input class="input" type="password" placeholder="Enter new password" />
          </label>
          <label class="field">
            Confirm Password
            <input class="input" type="password" placeholder="Confirm new password" />
          </label>
        </form>
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
.form-grid {
  display: grid;
  gap: 14px;
}
</style>
