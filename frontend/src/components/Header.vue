<template>
  <header class="header" :class="{ scrolled: isScrolled, 'animate-in': mounted }">
    <div class="header-container">
      <!-- Logo 区域 -->
      <router-link to="/" class="header-logo">
        <span>PPT生成器</span>
      </router-link>

      <!-- 桌面端导航 -->
      <nav class="header-nav">
        <ul class="nav-menu">
          <li class="nav-item">
            <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
              首页
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/settings" class="nav-link" :class="{ active: $route.path === '/settings' }">
              设置
            </router-link>
          </li>
        </ul>
      </nav>

      <!-- 用户操作区域 -->
      <div class="header-actions">
        <!-- 主题切换按钮 -->
        <button 
          class="theme-toggle"
          @click="toggleTheme"
          :title="isDarkMode ? '切换到浅色模式' : '切换到深色模式'"
          aria-label="切换主题"
        >
          <svg v-if="!isDarkMode" width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M12 3V4M12 20V21M4 12H3M6.31412 6.31412L5.5 5.5M17.6859 6.31412L18.5 5.5M6.31412 17.69L5.5 18.5L17.6859 17.69L18.5 18.5M21 12H20M16 12C16 14.2091 14.2091 16 12 16C9.79086 16 8 14.2091 8 12C8 9.79086 9.79086 8 12 8C14.2091 8 16 9.79086 16 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 移动端菜单按钮 -->
        <button 
          class="mobile-menu-toggle"
          :class="{ open: isMobileMenuOpen }"
          @click="toggleMobileMenu"
          aria-label="切换菜单"
        >
          <div class="hamburger">
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
          </div>
        </button>
      </div>
    </div>

    <!-- 移动端导航菜单 -->
    <nav class="mobile-nav" :class="{ open: isMobileMenuOpen }">
      <ul class="mobile-nav-menu">
        <li class="mobile-nav-item">
          <router-link 
            to="/" 
            class="mobile-nav-link" 
            :class="{ active: $route.path === '/' }"
            @click="closeMobileMenu"
          >
            首页
          </router-link>
        </li>
        <li class="mobile-nav-item">
          <router-link 
            to="/settings" 
            class="mobile-nav-link" 
            :class="{ active: $route.path === '/settings' }"
            @click="closeMobileMenu"
          >
            设置
          </router-link>
        </li>
      </ul>
      
      <!-- 移动端主题切换 -->
      <div class="mobile-theme-toggle">
        <button 
          class="btn btn-outline-secondary btn-sm w-full"
          @click="toggleTheme"
        >
          <svg v-if="!isDarkMode" width="16" height="16" viewBox="0 0 24 24" fill="none" class="mr-2">
            <path d="M12 3V4M12 20V21M4 12H3M6.31412 6.31412L5.5 5.5M17.6859 6.31412L18.5 5.5M6.31412 17.69L5.5 18.5L17.6859 17.69L18.5 18.5M21 12H20M16 12C16 14.2091 14.2091 16 12 16C9.79086 16 8 14.2091 8 12C8 9.79086 9.79086 8 12 8C14.2091 8 16 9.79086 16 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" class="mr-2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ isDarkMode ? '浅色模式' : '深色模式' }}
        </button>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mounted = ref(false)
const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)
const isDarkMode = ref(false)

// 检测滚动位置
const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}

// 切换移动菜单
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
  // 防止背景滚动
  if (isMobileMenuOpen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

// 关闭移动菜单
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
  document.body.style.overflow = ''
}

// 主题切换
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  updateTheme()
}

// 更新主题
const updateTheme = () => {
  const html = document.documentElement
  if (isDarkMode.value) {
    html.setAttribute('data-theme', 'dark')
    localStorage.setItem('theme', 'dark')
  } else {
    html.removeAttribute('data-theme')
    localStorage.setItem('theme', 'light')
  }
}

// 初始化主题
const initTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  
  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    isDarkMode.value = true
  } else {
    isDarkMode.value = false
  }
  
  updateTheme()
}

// 监听系统主题变化
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
const handleThemeChange = (e) => {
  if (!localStorage.getItem('theme')) {
    isDarkMode.value = e.matches
    updateTheme()
  }
}

// 监听路由变化关闭移动菜单
const unwatchRoute = route && route.path ? 
  (() => {
    let currentPath = route.path
    const checkRouteChange = () => {
      if (route.path !== currentPath) {
        currentPath = route.path
        closeMobileMenu()
      }
    }
    return { stop: () => {} } // 简化处理
  })() : { stop: () => {} }

onMounted(() => {
  mounted.value = true
  initTheme()
  
  // 添加事件监听
  window.addEventListener('scroll', handleScroll, { passive: true })
  mediaQuery.addEventListener('change', handleThemeChange)
  
  // 点击外部关闭移动菜单
  document.addEventListener('click', (e) => {
    const header = document.querySelector('.header')
    if (!header.contains(e.target) && isMobileMenuOpen.value) {
      closeMobileMenu()
    }
  })
  
  // ESC 键关闭移动菜单
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isMobileMenuOpen.value) {
      closeMobileMenu()
    }
  })
})

onUnmounted(() => {
  // 清理事件监听
  window.removeEventListener('scroll', handleScroll)
  mediaQuery.removeEventListener('change', handleThemeChange)
  
  // 恢复滚动
  document.body.style.overflow = ''
  
  // 停止路由监听
  if (unwatchRoute && typeof unwatchRoute.stop === 'function') {
    unwatchRoute.stop()
  }
})
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
}

.header a {
  text-decoration: none;
  color: var(--color-text-primary);
}

.header a:hover {
  color: var(--color-primary);
}
</style>