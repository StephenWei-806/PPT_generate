#!/bin/bash

# 前端构建脚本
# 用于本地开发和生产部署

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR"
BACKEND_STATIC_DIR="$SCRIPT_DIR/../backend/static/frontend"

echo "=== PPT生成器前端构建脚本 ==="

# 检查Node.js和npm
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm，请先安装npm"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "警告: Node.js版本过低 ($NODE_VERSION)，推荐使用16+"
fi

echo "Node.js版本: $(node --version)"
echo "npm版本: $(npm --version)"

# 进入前端目录
cd "$FRONTEND_DIR"

# 1. 清理旧文件
echo "1. 清理旧的构建文件..."
rm -rf dist
rm -rf "$BACKEND_STATIC_DIR"

# 2. 安装依赖
echo "2. 安装npm依赖..."
if [ ! -d "node_modules" ]; then
    echo "首次安装依赖..."
    npm install
else
    echo "更新依赖..."
    npm ci
fi

# 3. 构建生产版本
echo "3. 构建生产版本..."
export NODE_ENV=production
npm run build:production

# 4. 验证构建结果
echo "4. 验证构建结果..."
if [ -d "$BACKEND_STATIC_DIR" ]; then
    echo "✅ 构建成功！文件输出到: $BACKEND_STATIC_DIR"
    
    # 显示构建文件大小
    echo ""
    echo "构建文件列表:"
    find "$BACKEND_STATIC_DIR" -type f -exec ls -lh {} + | awk '{print $5 \"\\t\" $9}' | sort -k2
    
    # 计算总大小
    TOTAL_SIZE=$(du -sh "$BACKEND_STATIC_DIR" | cut -f1)
    echo ""
    echo "总大小: $TOTAL_SIZE"
    
    # 检查关键文件
    if [ -f "$BACKEND_STATIC_DIR/index.html" ]; then
        echo "✅ index.html 存在"
    else
        echo "❌ index.html 缺失"
        exit 1
    fi
    
    if [ -d "$BACKEND_STATIC_DIR/assets" ]; then
        echo "✅ assets 目录存在"
        ASSET_COUNT=$(find "$BACKEND_STATIC_DIR/assets" -type f | wc -l)
        echo "   包含 $ASSET_COUNT 个资源文件"
    else
        echo "❌ assets 目录缺失"
        exit 1
    fi
    
else
    echo "❌ 构建失败！输出目录不存在"
    exit 1
fi

# 5. 生成部署信息
echo "5. 生成部署信息..."
BUILD_TIME=$(date '+%Y-%m-%d %H:%M:%S')
BUILD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

cat > "$BACKEND_STATIC_DIR/build-info.json" << EOF
{
  "buildTime": "$BUILD_TIME",
  "buildHash": "$BUILD_HASH",
  "nodeVersion": "$(node --version)",
  "npmVersion": "$(npm --version)",
  "environment": "production"
}
EOF

echo "✅ 部署信息已生成"

echo ""
echo "=== 构建完成 ==="
echo "构建时间: $BUILD_TIME"
echo "提交哈希: $BUILD_HASH"
echo "输出目录: $BACKEND_STATIC_DIR"
echo ""
echo "下一步:"
echo "1. 将 backend/ 目录上传到服务器"
echo "2. 运行部署脚本: sudo ./deploy.sh"
echo "3. 访问: http://101.245.71.8/PPT_generate/"
echo ""