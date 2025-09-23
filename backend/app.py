from flask import Flask, jsonify, request
from routes.routes import ppt_bp

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
app.register_blueprint(ppt_bp, url_prefix='/ppt')

# 配置静态文件访问
from flask import send_from_directory
import os

@app.route('/PPT_generate/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'frontend'), filename)

@app.route('/PPT_generate/')
def serve_index():
    return send_from_directory(os.path.join(app.root_path, 'static', 'frontend'), 'index.html')

if __name__ == '__main__':
    try:
        app.run(debug=False, host='0.0.0.0', port=5001)
    except Exception as e:
        print(f'应用启动失败: {str(e)}')
        raise