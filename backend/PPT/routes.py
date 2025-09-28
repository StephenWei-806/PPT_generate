from flask import Blueprint, request, jsonify, current_app, Response, send_file, stream_with_context
import os
import time


from .ppt_service import PPTService
from .PPT_upload import ppt_upload_service
from utils.logger import ppt_logger
from utils.file_cleanup import file_cleanup_manager


# 创建Blueprint
ppt_bp = Blueprint('ppt', __name__, url_prefix='/ppt')

@ppt_bp.route('/download/<filename>', methods=['GET'])
def download_ppt(filename):
    """
    下载PPT文件
    """
    # PPT保存在backend/temp/generated目录下
    file_path = os.path.join(current_app.root_path, 'temp', 'generated', filename)
    
    ppt_logger.info(f"下载请求 - 文件名: {filename}")
    
    if not os.path.exists(file_path):
        ppt_logger.warning(f"下载失败 - 文件不存在: {file_path}")
        return jsonify({'error': '文件不存在'}), 404
    
    try:
        ppt_logger.info(f"下载成功 - 文件: {filename}")
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        ppt_logger.error(f"下载异常 - 文件: {filename} - 错误: {str(e)}")
        return jsonify({'error': '下载文件时出错'}), 500

@ppt_bp.route('/generate', methods=['POST'])
def generate_ppt():
    """
    生成PPT
    """
    template_file_path = None
    try:
        # 获取表单数据
        data = request.form.to_dict()
        
        # 提取参数
        input_content = data.get('inputContent', '')
        page_count = data.get('pageCount', 5)
        model = data.get('model', 'deepseek')
        api_key = data.get('apiKey', '')
        
        ppt_logger.info(f"PPT生成请求 - 页数: {page_count} - 模型: {model}")
        
        # 验证必要参数
        if not input_content or not api_key:
            ppt_logger.warning("PPT生成失败 - 缺少必要参数")
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 处理上传的模板文件
        if 'template' in request.files:
            template_file = request.files['template']
            if template_file and template_file.filename:
                # 使用上传服务处理文件
                try:
                    template_file_path = ppt_upload_service._save_template(template_file)
                except (ValueError, OSError) as e:
                    ppt_logger.warning(f"模板文件处理失败 - 文件名: {template_file.filename} - 错误: {str(e)}")
                    return jsonify({'error': str(e)}), 400
        
        # 调用PPT生成服务，传入模板文件路径
        ppt_logger.log_ppt_generation(
            input_content, page_count, model, 'start', template_file_path
        )
        
        generator = PPTService().generate_ppt_response(
            input_content, page_count, model, api_key, template_file_path
        )
        
        # 返回流式响应
        return Response(stream_with_context(generator()), mimetype='text/event-stream')
        
    except Exception as e:
        ppt_logger.error(f"PPT生成异常: {str(e)}")
        # 清理临时文件
        if template_file_path:
            ppt_upload_service.cleanup_file(template_file_path)
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@ppt_bp.route('/admin/cleanup', methods=['POST'])
def cleanup_temp_files():
    """
    手动清理临时文件
    """
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 1)
        
        cleaned_count, cleaned_size = file_cleanup_manager.cleanup_old_files_now(max_age_hours)
        
        return jsonify({
            'status': 'success',
            'message': f'清理完成，删除了 {cleaned_count} 个文件',
            'cleaned_count': cleaned_count,
            'cleaned_size': cleaned_size,
            'timestamp': time.time()
        })
    except Exception as e:
        ppt_logger.error(f"手动清理失败: {str(e)}")
        return jsonify({'error': f'清理失败: {str(e)}'}), 500