import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/dashboard',
      component: () => import('../views/DashboardView.vue'),
    },
    {
      path: '/market',
      component: () => import('../views/MarketView.vue'),
    },
    {
      path: '/trade',
      component: () => import('../views/TradeView.vue'),
    },
    {
      path: '/orders',
      component: () => import('../views/OrdersView.vue'),
    },
    {
      path: '/account',
      component: () => import('../views/AccountView.vue'),
    },
    {
      path: '/alerts',
      component: () => import('../views/AlertsView.vue'),
    },
    {
      path: '/settings',
      component: () => import('../views/SettingsView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('../views/NotFoundView.vue'),
    },
  ],
})

export default router
