import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Settings from '../views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory('/PPT_generate/'),
  routes
})

export default router