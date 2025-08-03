# PPT生成（填充）

## 项目简介
这是一个基于AI的PPT自动生成（填充）系统，最大的优点是——可以使用自己制作的PPT模板。系统会利用大语言模型(LLM)自动生成结构化的PPT内容，并基于模板创建完整的PPT文件。

## 功能特点
- 🚀 快速生成：输入内容描述，一键生成完整PPT
- 🎨 模板支持：支持上传自定义PPT模板
- 🧠 AI驱动：基于大语言模型生成专业内容
- ⚙️ 灵活配置：可设置PPT页数、选择不同LLM模型
- 🔄 实时预览：生成过程实时反馈，支持流式响应
- 📥 便捷下载：生成完成后可直接下载PPT文件

## 技术栈
- **后端**：Python + Flask + python-pptx
- **前端**：Vue.js + Vite + Pinia
- **AI模型**：支持通义千问(qwen-plus)、DeepSeek等
- **其他工具**：Flask-CORS、python-dotenv、requests

## 项目结构
```
PPT_generate/
├── .gitignore
├── README.md          # 项目说明文档
├── backend/           # 后端代码
│   ├── app.py         # Flask应用入口
│   ├── .env           # 环境变量配置
│   ├── requirements.txt # 依赖包列表
│   ├── routes/        # API路由
│   ├── services/      # 业务逻辑层
│   ├── utils/         # 工具函数
│   └── static/        # 静态文件(生成的PPT和前端构建文件)
└── frontend/          # 前端代码
    ├── index.html     # 入口HTML
    ├── package.json   # 前端依赖
    └── src/           # Vue.js源代码
        ├── App.vue    # 根组件
        ├── main.js    # 入口JS
        ├── router/    # 路由配置
        ├── store/     # 状态管理
        └── views/     # 视图组件
```

## 使用说明
### 1. 环境准备
1. 安装Python 3.8+和Node.js 16+
2. 克隆项目到本地
3. 安装后端依赖：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. 安装前端依赖：
   ```bash
   cd frontend
   npm install
   ```

### 2. 配置环境变量
在`backend/.env`文件中配置必要的API密钥：
```
# 默认模型
DEFAULT_MODEL=tongyi
# 通义千问API密钥
DASHSCOPE_API_KEY=your_api_key
# DeepSeek API密钥(可选)
DEEPSEEK_API_KEY=your_api_key
```

### 3. 启动项目
1. 先启动后端服务：
   ```bash
   cd backend
   python app.py
   ```
2. 再启动前端开发服务器：
   ```bash
   cd frontend
   npm run dev
   ```
3. 在浏览器中访问 http://localhost:5173/PPT_generate/

### 4. 生成PPT
1. 在首页输入PPT内容描述
2. 设置PPT页数(1-30)
3. 点击"生成PPT"按钮
4. 等待生成完成后，点击下载按钮获取PPT文件

## 注意事项
1. 本项目需要有效的LLM API密钥才能正常工作
2. 生成PPT的质量取决于输入内容的清晰度和完整性
3. 对于大型PPT(>20页)，生成时间可能会延长
4. 目前仅支持.pptx格式的模板上传

## 未来优化方向
- 添加更多PPT模板样式
- 支持图片和图表自动生成
- 优化LLM提示词，提高内容质量
- 添加用户认证和多用户支持
- 实现PPT在线预览功能

希望这个工具能帮助你节省制作PPT的时间，专注于内容创作！如果有任何问题或建议，欢迎提出。