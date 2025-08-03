<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'

const router = useRouter()

onMounted(() => {
  // 可以添加一些初始化逻辑
})
</script>

<template>
  <div class="app-container flex flex-col min-h-screen">
    <Header class="header" />
    <main class="main-content flex-1 container mx-auto px-4 py-8">
      <RouterView />
    </main>
    <Footer class="footer" />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
}
</style>
