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
                    <div v-if="generationProgress" class="progress-text">
                      {{ generationProgress }}
                    </div>
                  </div>
                  
                  <div v-if="streamContent && isGenerating" class="stream-content">
                    <div class="form-group">
                      <label class="form-label">实时输出</label>
                      <div class="stream-output">
                        <pre>{{ streamContent }}</pre>
                      </div>
                    </div>
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
                <div class="download-info">
                  <p class="download-filename">文件名：{{ downloadFilename }}</p>
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
const streamContent = ref('')
const generationStarted = ref(false)
const showDownloadButton = ref(false)
const downloadUrl = ref('')
const downloadFilename = ref('')
const isGenerating = ref(false)
const errors = ref({})
const isDragOver = ref(false)
const fileInput = ref(null)
const generationProgress = ref('')

// 计算属性
const canGenerate = computed(() => {
  return inputContent.value.trim().length > 0 && pageCount.value >= 1 && pageCount.value <= 30
})

// 文件大小验证
const validateFileSize = (file) => {
  const maxSize = 10 * 1024 * 1024 // 10MB
  return file.size <= maxSize
}

// 文件格式验证
const validateFileFormat = (file) => {
  return file.name.toLowerCase().endsWith('.pptx')
}

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
    if (!validateFileFormat(file)) {
      alert('请上传 .pptx 格式的文件')
      event.target.value = '' // 清空输入
      return
    }
    
    if (!validateFileSize(file)) {
      alert('文件大小不能超过10MB')
      event.target.value = '' // 清空输入
      return
    }
    
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
    
    if (!validateFileFormat(file)) {
      alert('请上传 .pptx 格式的文件')
      return
    }
    
    if (!validateFileSize(file)) {
      alert('文件大小不能超过10MB')
      return
    }
    
    templateFile.value = file
    // 更新文件输入框
    if (fileInput.value) {
      const dt = new DataTransfer()
      dt.items.add(file)
      fileInput.value.files = dt.files
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
  streamContent.value = ''
  generationProgress.value = ''
  showDownloadButton.value = false
  downloadUrl.value = ''
  downloadFilename.value = ''
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
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk
      
      // 处理缓冲区中的完整行
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留未完成的行
      
      for (const line of lines) {
        if (line.trim()) {
          let processedLine = line
          
          // 清理数据格式
          if (processedLine.startsWith('data: ')) {
            processedLine = processedLine.substring(6)
          }
          
          // 清理额外的换行符
          processedLine = processedLine.replace(/\n+$/, '')
          
          if (processedLine.trim()) {
            // 检查是否包含错误信息
            if (processedLine.includes('错误:') || processedLine.includes('ERROR:')) {
              streamContent.value += processedLine + '\n'
              fullResponseContent.value += processedLine + '\n'
              generationProgress.value = '生成失败'
              continue
            }
            
            // 处理PPT生成成功消息
            if (processedLine.includes('PPT生成成功: ')) {
              const parts = processedLine.split('PPT生成成功: ')
              if (parts.length > 1) {
                let filename = parts[1].trim()
                // 提取文件名（去除路径）
                const baseFilename = filename.split('/').pop().split('\\').pop()
                downloadFilename.value = baseFilename
                downloadUrl.value = `http://101.245.71.8/PPT_generate/ppt/download/${baseFilename}`
                showDownloadButton.value = true
                
                const displayMessage = parts[0] + 'PPT生成成功: ' + baseFilename
                streamContent.value += displayMessage + '\n'
                fullResponseContent.value += displayMessage + '\n'
                generationProgress.value = '生成完成'
              }
            } else {
              // 普通内容更新
              streamContent.value += processedLine + '\n'
              fullResponseContent.value += processedLine + '\n'
              
              // 更新生成进度提示
              if (processedLine.includes('JSON')) {
                generationProgress.value = '正在解析内容结构...'
              } else if (processedLine.includes('验证')) {
                generationProgress.value = '正在验证内容格式...'
              } else if (processedLine.includes('模板')) {
                generationProgress.value = '正在处理模板文件...'
              } else if (processedLine.includes('生成')) {
                generationProgress.value = '正在生成PPT文件...'
              }
            }
          }
        }
      }
    }
    
    // 处理缓冲区中剩余的内容
    if (buffer.trim()) {
      streamContent.value += buffer
      fullResponseContent.value += buffer
    }
    
  } catch (error) {
    console.error('生成PPT错误:', error)
    const errorMessage = '生成失败: ' + error.message
    streamContent.value += errorMessage + '\n'
    fullResponseContent.value += errorMessage + '\n'
    generationProgress.value = '生成失败'
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

