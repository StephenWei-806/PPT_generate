from flask import Flask, jsonify, request
from PPT import routes
from utils.file_cleanup import file_cleanup_manager
from utils.logger import ppt_logger
import atexit

app = Flask(__name__)
app.config['DEBUG'] = True
# 设置无超时限制
app.config['TIMEOUT'] = None
# 增加最大内容长度限制
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
# 配置CORS
from flask_cors import CORS
CORS(app, resources={
    r"/ppt/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/PPT_generate/ppt/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 注册蓝图
app.register_blueprint(routes.ppt_bp, url_prefix='/PPT_generate')
# 启动文件清理服务
file_cleanup_manager.start_cleanup_service(app.root_path)
ppt_logger.info("PPT应用初始化完成")

# 注册关闭时的清理函数
@atexit.register
def cleanup():
    ppt_logger.info("应用关闭，停止文件清理服务")
    file_cleanup_manager.stop_cleanup_service()

# 配置静态文件访问
from flask import send_from_directory
import os

@app.route('/PPT_generate/<path:filename>')
def serve_frontend(filename):
    response = send_from_directory(os.path.join(app.root_path, 'static', 'frontend'), filename)
    # 添加缓存控制头
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/PPT_generate/')
def serve_index():
    response = send_from_directory(os.path.join(app.root_path, 'static', 'frontend'), 'index.html')
    # 添加缓存控制头
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    try:
        app.run(debug=False, host='0.0.0.0', port=5001)
    except Exception as e:
        print(f'应用启动失败: {str(e)}')
        raise