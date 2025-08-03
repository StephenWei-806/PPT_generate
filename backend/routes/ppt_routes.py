from flask import Blueprint, request, jsonify, current_app, Response, send_file, stream_with_context
from werkzeug.utils import secure_filename
import os
from services.ppt_service import generate_ppt_response

ppt_bp = Blueprint('ppt', __name__)

@ppt_bp.route('/download/<filename>', methods=['GET'])
def download_ppt(filename):
    # 安全处理文件名
    safe_filename = secure_filename(filename)
    # 假设生成的PPT保存在backend/static目录下
    file_path = os.path.join(current_app.root_path, 'static', safe_filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    
    try:
        return send_file(file_path, as_attachment=True, download_name=safe_filename)
    except Exception as e:
        return jsonify({'error': '下载文件时出错'}), 500

@ppt_bp.route('/generate', methods=['POST'])
def generate_ppt():
    try:
        # 获取表单数据并打印
        data = request.form.to_dict()
        print("成功收到————————————————————————————————")
        # 提取参数
        input_content = data.get('inputContent', '')
        page_count = data.get('pageCount', 5)
        model = data.get('model', 'tongyi')
        api_key = data.get('apiKey', '')
        # 注意：不打印用户输入内容以保护隐私
        # 验证必要参数
        if not input_content or not api_key:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 验证页数参数
        try:
            page_count = int(page_count)
            if page_count < 1 or page_count > 30:
                return jsonify({'error': '页数必须在1-30之间'}), 400
        except ValueError:
            return jsonify({'error': '页数必须是有效的数字'}), 400
        
        # 调用PPT生成服务，获取生成器
        generator = generate_ppt_response(input_content, page_count, model, api_key)
        
        # 返回流式响应
        return Response(stream_with_context(generator()), mimetype='text/event-stream')
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500