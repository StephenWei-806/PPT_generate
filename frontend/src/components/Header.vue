<template>
  <header class="header flex items-center justify-between p-4 border-b border-gray-200 bg-white shadow-sm">
    <div class="container mx-auto flex items-center justify-between">
      <h1 class="text-xl font-bold" style="color: var(--primary-color)">PPT生成器</h1>
      <nav>
        <ul class="flex gap-6">
          <li><router-link to="/" class="px-3 py-1 hover:text-primary-color transition-colors">首页</router-link></li>
          <li><router-link to="/settings" class="px-3 py-1 hover:text-primary-color transition-colors">设置</router-link></li>
        </ul>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
}

.header a {
  text-decoration: none;
  color: var(--text-color);
}

.header a:hover {
  color: var(--primary-color);
}
</style>