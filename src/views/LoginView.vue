<template>
  <div class="login">
    <div class="login-left">
      <div class="login-brand">
        <span class="brand-dot"></span>
        Arbor Trade
      </div>
      <h1>Trade with clarity.</h1>
      <p class="login-copy">
        Monitor cash, holdings, and live orders in one unified trading client.
      </p>
      <div class="login-chips">
        <span class="chip">Realtime quotes</span>
        <span class="chip">Risk-aware limits</span>
        <span class="chip">Instant confirmations</span>
      </div>
      <div class="login-footnote">Central matching engine ready.</div>
    </div>

    <div class="login-card card">
      <h2>Sign in</h2>
      <p class="card-subtitle">Use your settlement account credentials.</p>
      <form class="login-form">
        <label class="field">
          Account ID
          <input class="input" placeholder="Enter account number" />
        </label>
        <label class="field">
          Trading Password
          <input class="input" type="password" placeholder="Enter password" />
        </label>
        <label class="field">
          Certificate
          <select class="select">
            <option>Primary certificate</option>
            <option>Backup certificate</option>
          </select>
        </label>
        <div class="login-actions">
          <button class="btn btn-ghost" type="button">Request access</button>
          <RouterLink class="btn btn-primary" to="/dashboard">Enter workspace</RouterLink>
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
  border-radius: 50%;
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
