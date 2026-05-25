<template>
  <div class="login">
    <div class="login-left">
      <div class="login-brand">
        <span class="brand-dot"></span>
        栖木交易
      </div>
      <h1>清晰掌控交易。</h1>
      <p class="login-copy">
        在统一的交易客户端中查看资金、持仓与委托。
      </p>
      <div class="login-chips">
        <span class="chip">实时行情</span>
        <span class="chip">限价风控</span>
        <span class="chip">成交回执</span>
      </div>
      <div class="login-footnote">撮合引擎已就绪</div>
    </div>

    <div class="login-card card">
      <h2>登录</h2>
      <p class="card-subtitle">使用资金账户登录。</p>
      <form class="login-form">
        <label class="field">
          账户号
          <input class="input" placeholder="请输入账户号" />
        </label>
        <label class="field">
          交易密码
          <input class="input" type="password" placeholder="请输入密码" />
        </label>
        <label class="field">
          安全证书
          <select class="select">
            <option>主证书</option>
            <option>备用证书</option>
          </select>
        </label>
        <div class="login-actions">
          <button class="btn btn-ghost" type="button">申请权限</button>
          <RouterLink class="btn btn-primary" to="/dashboard">进入工作台</RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  padding: 48px 10vw;
  position: relative;
  z-index: 1;
}

.login-left {
  display: flex;
  flex-direction: column;
  gap: 18px;
  justify-content: center;
}

.login-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.brand-dot {
  width: 14px;
  height: 14px;
  border-radius: 0;
  background: var(--accent);
}

.login-copy {
  font-size: 16px;
  color: var(--muted);
  max-width: 360px;
}

.login-chips {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.login-footnote {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.16em;
}

.login-card {
  max-width: 420px;
  align-self: center;
  padding: 28px;
}

.login-form {
  display: grid;
  gap: 14px;
}

.login-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

h1 {
  font-size: 40px;
  margin: 0;
}

h2 {
  margin: 0 0 6px;
}

@media (max-width: 720px) {
  .login {
    padding: 32px 20px;
  }

  h1 {
    font-size: 32px;
  }
}
</style>
