<template>
  <div class="settings-page">
    <div class="container">
      <div class="settings-wrapper">
        <div class="card card-lg">
          <div class="card-header">
            <h2 class="card-title">系统设置</h2>
            <p class="card-subtitle">配置您的PPT生成参数和偏好设置</p>
          </div>
          
          <div class="card-body">
            <form class="settings-form" @submit.prevent="saveSettings">
              <div class="form-section">
                <h3 class="section-title">基本设置</h3>
                
                <!-- API服务选择 -->
                <div class="form-group">
                  <label for="api" class="form-label required">API服务</label>
                  <select 
                    id="api"
                    v-model="settingsStore.selectedAPI"
                    class="form-select"
                    :class="{ 'is-invalid': errors.selectedAPI }"
                  >
                    <option 
                      v-for="api in settingsStore.availableAPIs" 
                      :key="api.value" 
                      :value="api.value"
                    >
                      {{ api.name }}
                    </option>
                  </select>
                  <div v-if="errors.selectedAPI" class="form-feedback invalid">
                    {{ errors.selectedAPI }}
                  </div>
                  <div class="form-help">
                    选择用于生成PPT内容的AI服务提供商
                  </div>
                </div>

                <!-- 默认页数设置 -->
                <div class="form-group">
                  <label for="pageCount" class="form-label required">默认PPT页数</label>
                  <input
                    type="number"
                    id="pageCount"
                    v-model.number="settingsStore.defaultPageCount"
                    min="1"
                    max="30"
                    step="1"
                    class="form-input"
                    :class="{ 'is-invalid': errors.defaultPageCount }"
                  />
                  <div v-if="errors.defaultPageCount" class="form-feedback invalid">
                    {{ errors.defaultPageCount }}
                  </div>
                  <div class="form-help">
                    设置新建 PPT 时的默认页数（范围：1-30）
                  </div>
                </div>

                <!-- API密钥设置 -->
                <div class="form-group">
                  <label for="apiKey" class="form-label required">API密钥</label>
                  <div class="input-group">
                    <input
                      :type="showApiKey ? 'text' : 'password'"
                      id="apiKey"
                      v-model="settingsStore.apiKey"
                      placeholder="输入API密钥"
                      class="form-input"
                      :class="{ 'is-invalid': errors.apiKey }"
                      autocomplete="off"
                    />
                    <div class="input-group-append">
                      <button 
                        type="button"
                        class="btn btn-outline-secondary btn-icon"
                        @click="toggleApiKeyVisibility"
                        :title="showApiKey ? '隐藏API密钥' : '显示API密钥'"
                      >
                        <svg v-if="!showApiKey" width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div v-if="errors.apiKey" class="form-feedback invalid">
                    {{ errors.apiKey }}
                  </div>
                  <div class="form-help">
                    您的API密钥将安全存储在本地，不会上传至服务器
                  </div>
                </div>
              </div>

              <div class="form-section">
                <h3 class="section-title">显示设置</h3>
                
                <!-- 主题设置 -->
                <div class="form-group">
                  <label class="form-label">界面主题</label>
                  <div class="theme-selector">
                    <div class="theme-options">
                      <label class="theme-option" :class="{ active: currentTheme === 'light' }">
                        <input 
                          type="radio" 
                          name="theme" 
                          value="light" 
                          v-model="currentTheme"
                          @change="updateTheme"
                          class="theme-radio"
                        >
                        <div class="theme-preview light-theme">
                          <div class="theme-header"></div>
                          <div class="theme-content">
                            <div class="theme-card"></div>
                            <div class="theme-card"></div>
                          </div>
                        </div>
                        <span class="theme-name">浅色模式</span>
                      </label>
                      
                      <label class="theme-option" :class="{ active: currentTheme === 'dark' }">
                        <input 
                          type="radio" 
                          name="theme" 
                          value="dark" 
                          v-model="currentTheme"
                          @change="updateTheme"
                          class="theme-radio"
                        >
                        <div class="theme-preview dark-theme">
                          <div class="theme-header"></div>
                          <div class="theme-content">
                            <div class="theme-card"></div>
                            <div class="theme-card"></div>
                          </div>
                        </div>
                        <span class="theme-name">深色模式</span>
                      </label>
                      
                      <label class="theme-option" :class="{ active: currentTheme === 'auto' }">
                        <input 
                          type="radio" 
                          name="theme" 
                          value="auto" 
                          v-model="currentTheme"
                          @change="updateTheme"
                          class="theme-radio"
                        >
                        <div class="theme-preview auto-theme">
                          <div class="theme-header"></div>
                          <div class="theme-content">
                            <div class="theme-card"></div>
                            <div class="theme-card"></div>
                          </div>
                        </div>
                        <span class="theme-name">跟随系统</span>
                      </label>
                    </div>
                  </div>
                  <div class="form-help">
                    选择界面的显示主题，跟随系统将根据操作系统设置自动切换
                  </div>
                </div>
              </div>
              
              <!-- 保存按钮 -->
              <div class="form-actions">
                <button 
                  type="submit"
                  class="btn btn-primary btn-lg"
                  :class="{ 'btn-loading': isSaving }"
                  :disabled="isSaving"
                >
                  <span v-if="!isSaving">保存设置</span>
                  <span v-else>保存中...</span>
                </button>
                
                <button 
                  type="button"
                  class="btn btn-outline-secondary btn-lg"
                  @click="resetSettings"
                  :disabled="isSaving"
                >
                  重置设置
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <!-- 设置提示信息 -->
        <div v-if="message.text" class="settings-message" :class="message.type">
          <div class="message-content">
            <svg v-if="message.type === 'success'" class="message-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="message.type === 'error'" class="message-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="message-text">{{ message.text }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useSettingsStore } from '../store'

// 初始化设置存储
const settingsStore = useSettingsStore()

// 响应式数据
const isSaving = ref(false)
const showApiKey = ref(false)
const currentTheme = ref('auto')
const errors = reactive({})
const message = reactive({
  text: '',
  type: 'success' // 'success' | 'error' | 'warning'
})

// 计算属性
const isFormValid = computed(() => {
  return settingsStore.selectedAPI && 
         settingsStore.apiKey && 
         settingsStore.defaultPageCount >= 1 && 
         settingsStore.defaultPageCount <= 30
})

// 方法
const toggleApiKeyVisibility = () => {
  showApiKey.value = !showApiKey.value
}

// 验证表单
const validateForm = () => {
  // 清空错误
  Object.keys(errors).forEach(key => {
    delete errors[key]
  })
  
  // 验证 API 服务
  if (!settingsStore.selectedAPI) {
    errors.selectedAPI = '请选择 API 服务'
  }
  
  // 验证 API 密钥
  if (!settingsStore.apiKey || settingsStore.apiKey.trim().length === 0) {
    errors.apiKey = '请输入 API 密钥'
  } else if (settingsStore.apiKey.length < 10) {
    errors.apiKey = 'API 密钥长度不能少于 10 位'
  }
  
  // 验证页数
  if (!settingsStore.defaultPageCount || settingsStore.defaultPageCount < 1 || settingsStore.defaultPageCount > 30) {
    errors.defaultPageCount = '页数必须在 1-30 之间'
  }
  
  return Object.keys(errors).length === 0
}

// 保存设置
const saveSettings = async () => {
  if (!validateForm()) {
    showMessage('请修复表单中的错误', 'error')
    return
  }
  
  isSaving.value = true
  
  try {
    // 保存设置
    settingsStore.saveSettings()
    
    // 模拟保存延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    showMessage('设置保存成功！', 'success')
    
  } catch (error) {
    console.error('保存设置失败:', error)
    showMessage('保存设置失败，请重试', 'error')
  } finally {
    isSaving.value = false
  }
}

// 重置设置
const resetSettings = () => {
  if (confirm('确定要重置所有设置吗？此操作不可撤销。')) {
    // 重置为默认值
    settingsStore.selectedAPI = 'tongyi'
    settingsStore.defaultPageCount = 10
    settingsStore.apiKey = ''
    currentTheme.value = 'auto'
    
    // 清空错误
    Object.keys(errors).forEach(key => {
      delete errors[key]
    })
    
    // 重置主题
    localStorage.removeItem('theme')
    updateTheme()
    
    showMessage('设置已重置为默认值', 'success')
  }
}

// 显示消息
const showMessage = (text, type = 'success') => {
  message.text = text
  message.type = type
  
  // 3秒后清空消息
  setTimeout(() => {
    message.text = ''
  }, 3000)
}

// 主题相关方法
const updateTheme = () => {
  const html = document.documentElement
  
  if (currentTheme.value === 'dark') {
    html.setAttribute('data-theme', 'dark')
    localStorage.setItem('theme', 'dark')
  } else if (currentTheme.value === 'light') {
    html.removeAttribute('data-theme')
    localStorage.setItem('theme', 'light')
  } else {
    // auto
    localStorage.removeItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      html.setAttribute('data-theme', 'dark')
    } else {
      html.removeAttribute('data-theme')
    }
  }
}

// 初始化主题
const initTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    currentTheme.value = 'dark'
  } else if (savedTheme === 'light') {
    currentTheme.value = 'light'
  } else {
    currentTheme.value = 'auto'
  }
  updateTheme()
}

// 组件挂载时加载设置
onMounted(() => {
  settingsStore.loadSettings()
  initTheme()
  
  // 监听系统主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleThemeChange = () => {
    if (currentTheme.value === 'auto') {
      updateTheme()
    }
  }
  
  mediaQuery.addEventListener('change', handleThemeChange)
  
  // 组件卸载时清理监听器
  return () => {
    mediaQuery.removeEventListener('change', handleThemeChange)
  }
})
</script>