<template>
  <div class="container mx-auto py-8">
    <!-- 模板上传区域 -->
    <div class="flex justify-center mb-8">
      <label class="flex flex-col items-center justify-center w-64 h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors">
        <div class="flex flex-col items-center justify-center pt-5 pb-6">
          <svg class="w-8 h-8 mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
          <p class="mb-2 text-sm text-gray-500"><span class="font-semibold">点击上传或拖放制作好的PPT模板</span></p>
          <p class="text-xs text-gray-500">支持 .pptx 格式</p>
        </div>
        <input type="file" accept=".pptx" class="hidden" @change="handleTemplateUpload" />
      </label>
    </div>

    <!-- 主要内容区域 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- 输入区域 -->
      <div class="card p-6 rounded-lg shadow-md bg-white">
        <h2 class="text-xl font-bold mb-4" style="color: var(--primary-color)">输入内容</h2>
        <textarea
          v-model="inputContent"
          placeholder="请输入PPT内容描述..."
          rows="8"
          class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-color/50"
        ></textarea>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div class="flex flex-col">
            <label for="pageCount" class="mb-1 text-sm font-medium text-gray-700">页数:</label>
            <input
              type="number"
              id="pageCount"
              v-model.number="pageCount"
              min="1"
              max="30"
              class="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-color/50"
            />
          </div>
          <div class="flex items-end">
            <button 
              @click="generatePPT"
              :disabled="isGenerating"
              class="w-full bg-primary-color hover:bg-primary-color/90 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="!isGenerating">生成PPT</span>
              <span v-if="isGenerating">生成中...</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 输出区域 -->
      <div class="card p-6 rounded-lg shadow-md bg-white">
        <!-- 完整响应内容文本框 -->
        <div>
          <h2 class="text-xl font-bold mb-4" style="color: var(--primary-color)">完整响应内容</h2>
          <textarea
            v-model="fullResponseContent"
            placeholder="完整的响应内容将显示在这里..."
            rows="12"
            readonly
            class="w-full p-3 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-color/50"
          ></textarea>
        </div>

        <!-- 下载按钮 -->
        <div v-if="showDownloadButton" class="mt-4 flex justify-end">
          <a 
            :href="downloadUrl"
            download
            class="inline-flex items-center px-4 py-2 bg-primary-color hover:bg-primary-color/90 text-white font-medium rounded-lg transition-colors"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
            下载PPT文件
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '../store'


// 状态管理
const settingsStore = useSettingsStore()
const inputContent = ref('')
const pageCount = ref(10)
const templateName = ref('')
const templateFile = ref(null)
const outputMessages = ref('')
const fullResponseContent = ref('') // 存储完整响应内容
const generationStarted = ref(false)
const showDownloadButton = ref(false)
const downloadUrl = ref('')
const isGenerating = ref(false)

// 处理模板上传
const handleTemplateUpload = (e) => {
  if (e.target.files.length > 0) {
    templateFile.value = e.target.files[0]
    templateName.value = templateFile.value.name
  }
}

// 生成PPT处理函数
const generatePPT = async () => {
  if (!inputContent.value.trim()) {
    outputMessages.value = ['错误: 请输入PPT内容描述']
    return
  }

  // 重置状态
  generationStarted.value = true
  outputMessages.value = ['开始生成PPT...']
  showDownloadButton.value = false
  isGenerating.value = true

  try {
    // 创建表单数据
    const formData = new FormData()
    formData.append('inputContent', inputContent.value)
    formData.append('pageCount', pageCount.value)
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
      throw new Error('生成PPT失败: ' + response.statusText)
    }

    // 处理流式响应
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          break
        }

        const chunk = decoder.decode(value, { stream: true })
        // 处理数据，去除前缀和结尾换行符
        let processedChunk = chunk;
        // 打印原始的 processedChunk，保留换行符
        console.log('原始 processedChunk:', processedChunk);
        if (processedChunk.startsWith('data: ')) {
          processedChunk = processedChunk.substring(6); // 去除 'data: '
        }
          // 去除结尾的两个换行符
          processedChunk = processedChunk.replace(/\n{2}$/, '').replace(/\n$/, '');

          // 处理PPT生成成功消息中的路径
          let displayChunk = processedChunk;
          if (processedChunk.includes('PPT生成成功: ')) {
            const parts = processedChunk.split('PPT生成成功: ');
            if (parts.length > 1) {
              let filename = parts[1].trim();
              const baseFilename = filename.split('/').pop().split('\\').pop();
              displayChunk = parts[0] + 'PPT生成成功: ' + baseFilename;
            }
          }

          // 添加处理后的内容
          outputMessages.value += displayChunk;
          fullResponseContent.value += displayChunk;

        // 检查是否包含下载信息
        if (chunk.includes('PPT生成成功: ')) {
          let filename = chunk.split('PPT生成成功: ')[1].trim()
          filename = filename.split('/').pop().split('\\').pop()
          downloadUrl.value = `http://101.245.71.8/PPT_generate/ppt/download/${filename}`
          showDownloadButton.value = true
        }
      }
  } catch (error) {
    outputMessages.value += '生成失败: ' + error.message
  } finally {
    isGenerating.value = false
  }
}
// 组件挂载时加载设置
onMounted(() => {
  settingsStore.loadSettings()
  // 从设置中加载默认页数
  pageCount.value = settingsStore.defaultPageCount
});
</script>

