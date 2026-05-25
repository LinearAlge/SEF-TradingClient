<script setup lang="ts">
import AppShell from '../components/AppShell.vue'
</script>

<template>
<<<<<<< HEAD
  <AppShell title="安全设置" subtitle="修改交易与取款密码">
    <template #actions>
      <button class="btn btn-ghost" type="button">验证证书</button>
      <button class="btn btn-primary" type="button">保存</button>
=======
  <AppShell title="Security Settings" subtitle="Update trading and withdrawal passwords">
    <template #actions>
      <button class="btn btn-ghost" type="button">Verify Certificate</button>
      <button class="btn btn-primary" type="button">Save Changes</button>
>>>>>>> origin/master
    </template>

    <section class="grid grid-2">
      <div class="card">
<<<<<<< HEAD
        <div class="card-title">交易密码</div>
        <div class="card-subtitle">下单时必填</div>
        <form class="form-grid">
          <label class="field">
            当前密码
            <input class="input" type="password" placeholder="请输入当前密码" />
          </label>
          <label class="field">
            新密码
            <input class="input" type="password" placeholder="请输入新密码" />
          </label>
          <label class="field">
            确认密码
            <input class="input" type="password" placeholder="请再次输入新密码" />
=======
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
>>>>>>> origin/master
          </label>
        </form>
      </div>
      <div class="card">
<<<<<<< HEAD
        <div class="card-title">取款密码</div>
        <div class="card-subtitle">取款时必填</div>
        <form class="form-grid">
          <label class="field">
            当前密码
            <input class="input" type="password" placeholder="请输入当前密码" />
          </label>
          <label class="field">
            新密码
            <input class="input" type="password" placeholder="请输入新密码" />
          </label>
          <label class="field">
            确认密码
            <input class="input" type="password" placeholder="请再次输入新密码" />
=======
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
>>>>>>> origin/master
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
