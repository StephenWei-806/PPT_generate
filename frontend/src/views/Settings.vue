<template>
  <div class="container mx-auto py-8">
    <div class="card p-6 rounded-lg shadow-md bg-white">
      <h2 class="text-xl font-bold mb-6" style="color: var(--primary-color)">系统设置</h2>
      <form class="space-y-6">
        <!-- API服务选择 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          <label class="text-sm font-medium text-gray-700">API服务</label>
          <select 
            v-model="settingsStore.selectedAPI"
            class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-color/50"
          >
            <option v-for="api in settingsStore.availableAPIs" :key="api.value" :value="api.value">{{ api.name }}</option>
          </select>
        </div>

        <!-- 默认页数设置 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          <label class="text-sm font-medium text-gray-700">默认PPT页数</label>
          <input
            type="number"
            v-model.number="settingsStore.defaultPageCount"
            min="1"
            max="30"
            class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-color/50"
          />
        </div>

        <!-- API密钥设置 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          <label class="text-sm font-medium text-gray-700">API密钥</label>
          <input
            type="password"
            v-model="settingsStore.apiKey"
            placeholder="输入API密钥"
            class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-color/50"
          />
        </div>

        <!-- 保存按钮 -->
        <div class="flex justify-end pt-4">
          <button 
            type="button"
            @click="saveSettings"
            class="bg-primary-color hover:bg-primary-color/90 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            保存设置
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSettingsStore } from '../store'

// 初始化设置存储
const settingsStore = useSettingsStore()

// 组件挂载时加载设置
onMounted(() => {
  settingsStore.loadSettings()
})

// 保存设置
const saveSettings = () => {
  settingsStore.saveSettings()
  alert('设置已保存！')
}
</script>