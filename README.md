# PPT生成（填充）

## 项目简介
这是一个基于AI的PPT自动生成（填充）系统，最大的优点是——可以使用自己制作的PPT模板。系统采用前后端分离架构，利用大语言模型(LLM)自动生成结构化的PPT内容，并支持基于自定义模板创建完整的PPT文件。

## 项目参考
1. Python 自动化教程(3) : 自动生成PPT文件 Part 1 （干货） https://blog.csdn.net/c80486/article/details/126434547

## 功能特点
- 🚀 **快速生成**：输入内容描述，一键生成完整PPT
- 🎨 **模板支持**：支持上传自定义PPT模板，支持拖放上传
- 🧠 **AI驱动**：基于大语言模型生成专业内容，支持通义千问、DeepSeek等多种模型
- ⚙️ **灵活配置**：可设置PPT页数(1-30页)，选择不同LLM模型
- 🔄 **实时预览**：生成过程实时反馈，支持流式响应
- 📥 **便捷下载**：生成完成后可直接下载PPT文件
- 📁 **文件管理**：自动清理临时文件，支持手动清理和文件统计
- 🔒 **安全验证**：严格的文件格式验证和安全性检查

## 技术栈
- **后端**：Python 3.8+ + Flask + python-pptx + OpenAI SDK
- **前端**：Vue.js 3 + Vite + Pinia + Vue Router
- **AI模型**：支持通义千问(qwen-plus)、DeepSeek(deepseek-chat)等
- **其他工具**：Flask-CORS、python-dotenv、requests、httpx、Gunicorn

## 项目结构
```
PPT_generate/
├── .gitignore
├── README.md              # 项目说明文档
├── DEPLOYMENT.md          # 部署说明文档
├── TROUBLESHOOTING.md     # 问题排查指南
├── deploy.py              # Python部署脚本
├── deploy.bat             # Windows部署脚本
├── deploy.sh              # Linux/Mac部署脚本
├── test_deployment.py     # 部署验证测试
├── backend/               # 后端代码
│   ├── app.py             # Flask应用入口
│   ├── requirements.txt   # 依赖包列表
│   ├── PPT/               # 主要业务逻辑
│   │   ├── routes.py      # API路由
│   │   ├── llm_service.py # LLM服务
│   │   ├── ppt_service.py # PPT生成服务
│   │   └── PPT_upload.py  # PPT文件上传服务
│   ├── utils/             # 工具函数
│   │   ├── logger.py      # 日志系统
│   │   ├── file_cleanup.py # 文件清理管理
│   │   ├── json_utils.py  # JSON工具
│   │   └── ppt_utils.py   # PPT工具
│   ├── temp/              # 临时文件目录
│   │   ├── uploads/       # 上传文件
│   │   ├── generated/     # 生成文件
│   │   └── default/       # 默认模板
│   └── static/            # 静态文件
│       └── frontend/      # 前端构建文件
└── frontend/              # 前端代码
    ├── index.html         # 入口HTML
    ├── package.json       # 前端依赖
    ├── vite.config.js     # Vite配置
    └── src/               # Vue.js源代码
        ├── App.vue        # 根组件
        ├── main.js        # 入口JS
        ├── style.css      # 全局样式
        ├── router/        # 路由配置
        ├── store/         # 状态管理(Pinia)
        ├── views/         # 视图组件
        ├── components/    # 公共组件
        └── assets/        # 静态资源(样式、图片等)
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

#### 开发模式：
1. 先启动后端服务：
   ```bash
   cd backend
   python app.py
   ```
   后端服务将在 http://localhost:5001 运行

2. 再启动前端开发服务器：
   ```bash
   cd frontend
   npm run dev
   ```
   前端开发服务器将在 http://localhost:5173 运行

3. 在浏览器中访问 http://localhost:5173/PPT_generate/

### 4. 生成PPT
1. 在首页输入PPT内容描述
2. 设置PPT页数(1-30)
3. 点击"生成PPT"按钮
4. 等待生成完成后，点击下载按钮获取PPT文件

## 注意事项
1. **API密钥配置**：本项目需要有效的LLM API密钥才能正常工作
2. **内容质量**：生成PPT的质量取决于输入内容的清晰度和完整性
3. **生成时间**：对于大型PPT(>20页)，生成时间可能会延长
4. **文件格式**：目前仅支持.pptx格式的模板上传
5. **文件大小**：上传模板文件大小限制为10MB
6. **文件清理**：系统会自动清理超过1小时的临时文件
7. **端口配置**：后端默认端口为5001，前端开发端口为5173

## 优化方向
- 添加更多PPT模板样式和主题
- 支持图片和图表自动生成
- 优化LLM提示词，提高内容质量
- 添加用户认证和多用户支持
- 实现PPT在线预览功能
<<<<<<< HEAD
=======
- 支持更多文件格式(.ppt、.odp等)
- 添加批量生成和模板管理功能
- 集成更多LLM提供商（ChatGPT、文心一言等）
- 添加性能监控和错误追踪
- 实现分布式部署和负载均衡


希望这个工具能帮助您节省制作PPT的时间，专注于内容创作！如果有任何问题或建议，欢迎提出。
