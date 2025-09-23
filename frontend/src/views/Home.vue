<template>
  <div class="home-page">
    <div class="container">
      <!-- 模板上传区域 -->
      <section class="upload-section">
        <div class="upload-wrapper">
          <label 
            class="file-upload-area"
            :class="{ 
              'drag-over': isDragOver,
              'has-file': templateFile 
            }"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
          >
            <div class="upload-content">
              <div class="upload-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="upload-text">
                <h3 class="upload-title">
                  {{ templateFile ? templateFile.name : '上传PPT模板' }}
                </h3>
                <p class="upload-subtitle">
                  {{ templateFile ? '点击重新选择文件' : '点击上传或拖放制作好的PPT模板' }}
                </p>
                <small class="upload-note">支持 .pptx 格式</small>
              </div>
            </div>
            <input 
              type="file" 
              accept=".pptx" 
              class="hidden" 
              @change="handleTemplateUpload" 
              ref="fileInput"
            />
          </label>
        </div>
      </section>

      <!-- 主要内容区域 -->
      <section class="main-section">
        <div class="content-grid">
          <!-- 输入区域 -->
          <div class="input-section">
            <div class="card card-lg">
              <div class="card-header">
                <h2 class="card-title">输入内容</h2>
                <p class="card-subtitle">请描述您希望生成的PPT内容</p>
              </div>
              <div class="card-body">
                <div class="form-group">
                  <label for="content" class="form-label">内容描述</label>
                  <textarea
                    id="content"
                    v-model="inputContent"
                    placeholder="请输入PPT内容描述..."
                    rows="8"
                    class="form-textarea"
                    :class="{ 'is-invalid': errors.content }"
                  ></textarea>
                  <div v-if="errors.content" class="form-feedback invalid">
                    {{ errors.content }}
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="col-12 md:col-6">
                    <div class="form-group">
                      <label for="pageCount" class="form-label">页数</label>
                      <input
                        type="number"
                        id="pageCount"
                        v-model.number="pageCount"
                        min="1"
                        max="30"
                        class="form-input"
                        :class="{ 'is-invalid': errors.pageCount }"
                      />
                      <div v-if="errors.pageCount" class="form-feedback invalid">
                        {{ errors.pageCount }}
                      </div>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="form-group">
                      <label class="form-label">&nbsp;</label>
                      <button 
                        @click="generatePPT"
                        :disabled="isGenerating || !canGenerate"
                        class="btn btn-primary btn-lg w-full"
                        :class="{ 'btn-loading': isGenerating }"
                      >
                        <span v-if="!isGenerating">生成PPT</span>
                        <span v-else>生成中...</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输出区域 -->
          <div class="output-section">
            <div class="card card-lg">
              <div class="card-header">
                <h2 class="card-title">输出结果</h2>
                <p class="card-subtitle">生成的PPT内容将显示在这里</p>
              </div>
              <div class="card-body">
                <div class="output-content" :class="{ 'is-loading': isGenerating }">
                  <div v-if="!generationStarted && !fullResponseContent" class="empty-state">
                    <div class="empty-icon">
                      <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </div>
                    <h3 class="empty-title">待生成</h3>
                    <p class="empty-description">请先输入内容再点击生成PPT</p>
                  </div>
                  
                  <div v-if="isGenerating" class="loading-state">
                    <div class="loading-spinner"></div>
                    <p class="loading-text">正在生成PPT，请稍候...</p>
                  </div>
                  
                  <div v-if="fullResponseContent && !isGenerating" class="result-content">
                    <div class="form-group">
                      <label class="form-label">完整响应内容</label>
                      <textarea
                        v-model="fullResponseContent"
                        placeholder="完整的响应内容将显示在这里..."
                        rows="12"
                        readonly
                        class="form-textarea result-textarea"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 下载按钮 -->
              <div v-if="showDownloadButton" class="card-footer">
                <a 
                  :href="downloadUrl"
                  download
                  class="btn btn-success btn-lg"
                >
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                  </svg>
                  下载PPT文件
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSettingsStore } from '../store'

// 状态管理
const settingsStore = useSettingsStore()
const inputContent = ref('')
const pageCount = ref(10)
const templateFile = ref(null)
const outputMessages = ref('')
const fullResponseContent = ref('')
const generationStarted = ref(false)
const showDownloadButton = ref(false)
const downloadUrl = ref('')
const isGenerating = ref(false)
const errors = ref({})
const isDragOver = ref(false)
const fileInput = ref(null)

// 计算属性
const canGenerate = computed(() => {
  return inputContent.value.trim().length > 0 && pageCount.value >= 1 && pageCount.value <= 30
})

// 验证表单
const validateForm = () => {
  errors.value = {}
  
  if (!inputContent.value.trim()) {
    errors.value.content = '请输入PPT内容描述'
  }
  
  if (pageCount.value < 1 || pageCount.value > 30) {
    errors.value.pageCount = '页数必须在 1-30 之间'
  }
  
  return Object.keys(errors.value).length === 0
}

// 处理文件上传
const handleTemplateUpload = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    templateFile.value = file
  }
}

// 拖放事件处理
const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    if (file.name.endsWith('.pptx')) {
      templateFile.value = file
      // 更新文件输入框
      if (fileInput.value) {
        const dt = new DataTransfer()
        dt.items.add(file)
        fileInput.value.files = dt.files
      }
    } else {
      alert('请上传 .pptx 格式的文件')
    }
  }
}

// 生成PPT处理函数
const generatePPT = async () => {
  if (!validateForm()) {
    return
  }

  // 重置状态
  generationStarted.value = true
  outputMessages.value = ''
  fullResponseContent.value = ''
  showDownloadButton.value = false
  isGenerating.value = true
  errors.value = {}

  try {
    // 创建表单数据
    const formData = new FormData()
    formData.append('inputContent', inputContent.value)
    formData.append('pageCount', pageCount.value.toString())
    formData.append('model', settingsStore.selectedAPI)
    formData.append('apiKey', settingsStore.apiKey)

    // 如果有模板文件，添加到表单数据
    if (templateFile.value) {
      formData.append('template', templateFile.value)
    }

    // 发送生成请求
    const response = await fetch('http://101.245.71.8/PPT_generate/ppt/generate', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`生成PPT失败: ${response.statusText}`)
    }

    // 处理流式响应
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法读取响应数据')
    }
    
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      // 处理数据，去除前缀和结尾换行符
      let processedChunk = chunk
      
      if (processedChunk.startsWith('data: ')) {
        processedChunk = processedChunk.substring(6) // 去除 'data: '
      }
      
      // 去除结尾的换行符
      processedChunk = processedChunk.replace(/\n{2}$/, '').replace(/\n$/, '')

      // 处理PPT生成成功消息中的路径
      let displayChunk = processedChunk
      if (processedChunk.includes('PPT生成成功: ')) {
        const parts = processedChunk.split('PPT生成成功: ')
        if (parts.length > 1) {
          let filename = parts[1].trim()
          const baseFilename = filename.split('/').pop().split('\\').pop()
          displayChunk = parts[0] + 'PPT生成成功: ' + baseFilename
        }
      }

      // 添加处理后的内容
      outputMessages.value += displayChunk
      fullResponseContent.value += displayChunk

      // 检查是否包含下载信息
      if (chunk.includes('PPT生成成功: ')) {
        let filename = chunk.split('PPT生成成功: ')[1]?.trim()
        if (filename) {
          filename = filename.split('/').pop().split('\\').pop()
          downloadUrl.value = `http://101.245.71.8/PPT_generate/ppt/download/${filename}`
          showDownloadButton.value = true
        }
      }
    }
  } catch (error) {
    console.error('生成PPT错误:', error)
    fullResponseContent.value = '生成失败: ' + error.message
    errors.value.general = error.message
  } finally {
    isGenerating.value = false
  }
}

// 组件挂载时加载设置
onMounted(() => {
  settingsStore.loadSettings()
  // 从设置中加载默认页数
  pageCount.value = settingsStore.defaultPageCount
})
</script>

