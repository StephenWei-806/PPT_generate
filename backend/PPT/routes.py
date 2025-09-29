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

@ppt_bp.route('/upload-template', methods=['POST'])
def upload_template():
    """
    上传PPT模板文件
    """
    try:
        # 检查是否有文件上传
        if 'template' not in request.files:
            return jsonify({'error': '没有上传模板文件'}), 400
        
        template_file = request.files['template']
        if not template_file or not template_file.filename:
            return jsonify({'error': '没有选择文件'}), 400
        
        # 使用上传服务处理文件
        try:
            template_file_path = ppt_upload_service._save_template(template_file)
            filename = os.path.basename(template_file_path)
            
            ppt_logger.info(f"模板文件上传成功: {filename}")
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': '模板文件上传成功'
            })
            
        except (ValueError, OSError) as e:
            ppt_logger.warning(f"模板文件处理失败 - 文件名: {template_file.filename} - 错误: {str(e)}")
            return jsonify({'error': str(e)}), 400
            
    except Exception as e:
        ppt_logger.error(f"模板文件上传异常: {str(e)}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500



@ppt_bp.route('/stream', methods=['POST'])
def stream_llm_response():
    """
    第一阶段：流式输出LLM响应内容
    """
    try:
        # 获取表单数据
        data = request.form.to_dict()
        
        # 提取参数
        input_content = data.get('inputContent', '')
        page_count = int(data.get('pageCount', 5))  # 转换为整数
        model = data.get('model', 'deepseek')
        api_key = data.get('apiKey', '')
        
        ppt_logger.info(f"LLM流式响应请求 - 页数: {page_count} - 模型: {model}")
        
        # 验证必要参数
        if not input_content or not api_key:
            ppt_logger.warning("LLM流式响应失败 - 缺少必要参数")
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 创建PPT服务实例
        ppt_service = PPTService()
        
        # 获取流式响应生成器和内容容器
        stream_generator, full_content_container = ppt_service.stream_llm_content(
            input_content, page_count, model, api_key
        )
        
        # 定义流式响应函数
        def llm_stream():
            try:
                # 流式输出LLM内容
                for chunk in stream_generator():
                    yield chunk
                
                # 检查是否收到完整内容
                full_chunk = full_content_container['content']
                if not full_chunk.strip():
                    yield "错误: 未收到有效的LLM响应内容\n"
                    return
                
                # 流式响应完成标记
                yield "STREAM_COMPLETE\n"
                    
            except Exception as e:
                ppt_logger.error(f"LLM流式响应异常: {str(e)}")
                yield f"流式响应异常: {str(e)}\n"
        
        # 记录流式响应开始
        ppt_logger.info(f"开始LLM流式响应 - 内容长度: {len(input_content)}")
        
        # 返回流式响应
        return Response(stream_with_context(llm_stream()), mimetype='text/event-stream')
        
    except Exception as e:
        ppt_logger.error(f"LLM流式响应异常: {str(e)}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500


@ppt_bp.route('/generate', methods=['POST'])
def generate_ppt():
    """
    第二阶段：基于完整内容生成PPT
    """
    template_file_path = None
    try:
        # 获取JSON数据
        data = request.get_json()
        if not data:
            ppt_logger.warning("PPT生成失败 - 无效的JSON数据")
            return jsonify({'error': '无效的请求数据'}), 400
        
        # 提取参数
        full_content = data.get('fullContent', '')
        input_content = data.get('inputContent', '')
        page_count = data.get('pageCount', 5)
        model = data.get('model', 'deepseek')
        template_info = data.get('templateInfo', {})
        
        ppt_logger.info(f"PPT生成请求 - 页数: {page_count} - 模型: {model} - 内容长度: {len(full_content)}")
        
        # 验证必要参数
        if not full_content or not input_content:
            ppt_logger.warning("PPT生成失败 - 缺少必要参数")
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 处理模板文件信息
        if template_info.get('hasTemplate'):
            template_filename = template_info.get('filename')
            if template_filename:
                # 构建模板文件路径（假设已经上传到临时目录）
                template_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp', 'uploads', template_filename)
                if not os.path.exists(template_file_path):
                    ppt_logger.warning(f"模板文件不存在: {template_file_path}")
                    template_file_path = None
        
        # 创建PPT服务实例
        ppt_service = PPTService()
        
        try:
            # 生成PPT
            result_file = ppt_service.generate_ppt_from_content(
                full_content, input_content, page_count, model, template_file_path
            )
            
            # 生成成功，提取文件名
            filename = os.path.basename(result_file)
            
            ppt_logger.info(f"PPT生成成功: {filename}")
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'PPT生成成功'
            })
            
        except Exception as ppt_error:
            ppt_logger.error(f"PPT生成失败: {str(ppt_error)}")
            # 生成失败，清理模板文件
            if template_file_path:
                try:
                    ppt_upload_service.cleanup_file(template_file_path)
                except Exception as cleanup_error:
                    ppt_logger.warning(f"清理模板文件失败: {str(cleanup_error)}")
            
            return jsonify({
                'success': False,
                'error': str(ppt_error)
            }), 500
        
    except Exception as e:
        ppt_logger.error(f"PPT生成异常: {str(e)}")
        # 生成异常时清理模板文件
        if template_file_path:
            try:
                ppt_upload_service.cleanup_file(template_file_path)
            except Exception as cleanup_error:
                ppt_logger.warning(f"清理模板文件失败: {str(cleanup_error)}")
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