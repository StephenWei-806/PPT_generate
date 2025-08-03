import { createPinia, defineStore } from 'pinia'

// 创建Pinia实例
const pinia = createPinia()

// 定义设置存储
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    selectedAPI: 'tongyi',
    defaultPageCount: 10,
    apiKey: '',
    availableAPIs: [
      { value: 'tongyi', name: '通义千问 (使用 qwen-plus 模型)' },
      { value: 'deepseek', name: 'DeepSeek (使用 deepseek-chat 模型)' }
    ]
    
  }),
  actions: {
    // 保存设置到本地存储
    saveSettings() {
      const settings = {
        selectedAPI: this.selectedAPI,
        defaultPageCount: this.defaultPageCount,
        apiKey: this.apiKey
      }
      localStorage.setItem('pptSettings', JSON.stringify(settings))
    },
    // 从本地存储加载设置
    loadSettings() {
      const savedSettings = localStorage.getItem('pptSettings')
      if (savedSettings) {
        const settings = JSON.parse(savedSettings)
        this.selectedAPI = settings.selectedAPI || 'tongyi'
        this.defaultPageCount = settings.defaultPageCount || 10
        this.apiKey = settings.apiKey || ''
      }
    }
  }
})

export default pinia