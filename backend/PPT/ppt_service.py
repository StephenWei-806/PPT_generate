import json
import re
import os

from .llm_service import LLMService
from utils.ppt_utils import replace_text_in_ppt
from utils.json_utils import extract_json_from_text, validate_ppt_json
from utils.logger import ppt_logger

class PPTService:
    """
    PPT服务类，用于生成PPT内容和处理相关操作
    """
    
    def stream_llm_content(self, input_content, page_count, model, api_key):
        """流式生成LLM内容
        
        Args:
            input_content (str): 输入内容
            page_count (int): PPT页数
            model (str): 使用的LLM模型
            api_key (str): API密钥
        return:
            tuple: (生成器函数, 完整内容存储容器)
        """
        full_content_container = {'content': '', 'error': None, 'status': 'pending'}
        
        def stream_generator():
            nonlocal page_count  # 允许修改外部参数
            try:
                # 参数验证
                if not input_content or not input_content.strip():
                    error_msg = "错误: 输入内容不能为空\n"
                    full_content_container['error'] = error_msg
                    full_content_container['status'] = 'error'
                    ppt_logger.warning("参数验证失败: 输入内容为空")
                    yield error_msg
                    return
                
                if not api_key or not api_key.strip():
                    error_msg = "错误: API密钥不能为空\n"
                    full_content_container['error'] = error_msg
                    full_content_container['status'] = 'error'
                    ppt_logger.warning("参数验证失败: API密钥为空")
                    yield error_msg
                    return
                
                # 类型转换和验证
                try:
                    if isinstance(page_count, str):
                        page_count = int(page_count)
                    elif not isinstance(page_count, int):
                        page_count = int(page_count)
                except (ValueError, TypeError):
                    error_msg = f"错误: PPT页数必须为数字，当前值: {page_count}\n"
                    full_content_container['error'] = error_msg
                    full_content_container['status'] = 'error'
                    ppt_logger.warning(f"参数验证失败: 页数类型错误 {page_count}")
                    yield error_msg
                    return
                
                if page_count <= 0 or page_count > 30:
                    error_msg = f"错误: PPT页数必须在 1-30 之间，当前值: {page_count}\n"
                    full_content_container['error'] = error_msg
                    full_content_container['status'] = 'error'
                    ppt_logger.warning(f"参数验证失败: 页数超出范围 {page_count}")
                    yield error_msg
                    return
                
                full_content_container['status'] = 'streaming'
                ppt_logger.info(f"开始LLM流式请求 - 内容长度: {len(input_content)}, 页数: {page_count}, 模型: {model}")
                
                # 调用LLM服务生成内容
                llm_service = LLMService()
                chunk_count = 0
                
                for chunk in llm_service.call_llm_api(input_content, page_count, model=model, api_key=api_key):
                    chunk_count += 1
                    
                    # 检查是否是错误信息
                    if chunk.startswith("ERROR:"):
                        error_msg = f"错误: {chunk[6:]}建议检查API密钥和网络连接\n"
                        full_content_container['error'] = error_msg
                        full_content_container['status'] = 'error'
                        ppt_logger.error(f"LLM API调用错误: {chunk[6:]}")
                        yield error_msg
                        return
                    
                    # 清理数据格式，移除'data: '前缀
                    clean_chunk = re.sub(r'^(data:\s*)+', '', chunk.strip(), flags=re.MULTILINE)
                    
                    # 累积完整内容
                    full_content_container['content'] += clean_chunk
                    
                    # 实时输出
                    yield clean_chunk
                
                # 检查是否收到了有效内容
                if not full_content_container['content'].strip():
                    error_msg = "错误: 未收到LLM响应内容，请检查API密钥和网络连接\n"
                    full_content_container['error'] = error_msg
                    full_content_container['status'] = 'error'
                    ppt_logger.error(f"LLM响应异常: 未收到有效内容，共处理 {chunk_count} 个数据块")
                    yield error_msg
                    return
                
                full_content_container['status'] = 'completed'
                ppt_logger.info(f"LLM流式响应完成，内容长度: {len(full_content_container['content'])}，处理数据块: {chunk_count}")
                
            except ConnectionError as e:
                error_msg = f"LLM流式响应网络错误: {str(e)}\n"
                full_content_container['error'] = error_msg
                full_content_container['status'] = 'error'
                ppt_logger.error(f"网络连接错误: {str(e)}")
                yield error_msg
            except TimeoutError as e:
                error_msg = f"LLM流式响应超时: {str(e)}\n"
                full_content_container['error'] = error_msg
                full_content_container['status'] = 'error'
                ppt_logger.error(f"请求超时: {str(e)}")
                yield error_msg
            except Exception as e:
                error_msg = f"LLM流式响应异常: {str(e)}\n"
                full_content_container['error'] = error_msg
                full_content_container['status'] = 'error'
                ppt_logger.error(f"流式响应未知错误: {str(e)}", exc_info=True)
                yield error_msg
        
        return stream_generator, full_content_container
    
    def generate_ppt_from_content(self, full_content, input_content, page_count, model, template_path=None):
        """基于完整内容生成PPT
        
        Args:
            full_content (str): LLM生成的完整内容
            input_content (str): 原始输入内容（用于日志）
            page_count (int): PPT页数（用于日志）
            model (str): 使用的模型（用于日志）
            template_path (str, optional): 模板文件路径
        return:
            str: 生成的PPT文件路径
        """
        try:
            # 参数验证
            if not full_content or not full_content.strip():
                error_msg = "PPT生成失败: 内容为空"
                ppt_logger.error(error_msg)
                raise ValueError(error_msg)
            
            ppt_logger.info(f"开始PPT生成 - 内容长度: {len(full_content)}")
            
            # 清理Markdown代码块格式
            clean_content = full_content.replace('```json', '').replace('```', '').strip()
            
            # 尝试从文本中提取JSON
            try:
                json_str = extract_json_from_text(clean_content)
                if not json_str.strip():
                    raise ValueError("未能从内容中提取到有效的JSON数据")
                
                json_data = json.loads(json_str)
                ppt_logger.info(f"JSON解析成功 - 包含键: {list(json_data.keys())[:10]}...")  # 只显示前10个键
                
            except json.JSONDecodeError as e:
                error_msg = f"JSON解析失败: {str(e)}。内容预览: {clean_content[:200]}..."
                ppt_logger.error(error_msg)
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'failed', 
                    template_path, None, f"JSON解析错误: {str(e)}"
                )
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"JSON提取失败: {str(e)}。内容预览: {clean_content[:200]}..."
                ppt_logger.error(error_msg)
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'failed', 
                    template_path, None, f"JSON提取错误: {str(e)}"
                )
                raise Exception(error_msg)
            
            # 验证JSON结构是否符合PPT要求
            try:
                validate_ppt_json(json_data)
                ppt_logger.info("JSON结构验证通过")
            except Exception as e:
                error_msg = f"JSON结构验证失败: {str(e)}。请检查必要字段是否存在"
                ppt_logger.error(error_msg)
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'failed', 
                    template_path, None, f"JSON验证错误: {str(e)}"
                )
                raise Exception(error_msg)
            
            # 选择模板文件路径
            try:
                selected_template = self._select_template_path(template_path)
                ppt_logger.info(f"使用模板文件: {selected_template}")
            except FileNotFoundError as e:
                error_msg = f"模板文件错误: {str(e)}"
                ppt_logger.error(error_msg)
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'failed', 
                    template_path, None, f"模板文件错误: {str(e)}"
                )
                raise Exception(error_msg)
            
            # 生成PPT
            try:
                result_file = replace_text_in_ppt(json.dumps(json_data), selected_template)
                
                if not result_file or not os.path.exists(result_file):
                    raise Exception("生成的PPT文件不存在")
                
                # 检查文件大小
                file_size = os.path.getsize(result_file)
                if file_size < 1024:  # 小于1KB可能是空文件
                    raise Exception(f"生成的PPT文件太小: {file_size} bytes")
                
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'success', 
                    selected_template, result_file
                )
                
                ppt_logger.info(f"PPT生成成功 - 文件: {result_file}, 大小: {file_size} bytes")
                return result_file
                
            except PermissionError as e:
                error_msg = f"PPT文件写入权限错误: {str(e)}"
                ppt_logger.error(error_msg)
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'failed', 
                    selected_template, None, error_msg
                )
                raise Exception(error_msg)
            except FileNotFoundError as e:
                error_msg = f"PPT模板文件不存在: {str(e)}"
                ppt_logger.error(error_msg)
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'failed', 
                    selected_template, None, error_msg
                )
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"PPT生成失败: {str(e)}"
                ppt_logger.error(error_msg, exc_info=True)
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'failed', 
                    selected_template, None, error_msg
                )
                raise Exception(error_msg)
            
        except ValueError as e:
            # 参数验证错误
            ppt_logger.warning(f"参数验证错误: {str(e)}")
            raise Exception(f"参数错误: {str(e)}")
        except Exception as e:
            # 捕获所有其他异常
            if not str(e).startswith("PPT生成失败") and not str(e).startswith("JSON"):
                error_msg = f"PPT生成未知错误: {str(e)}"
                ppt_logger.error(error_msg, exc_info=True)
                raise Exception(error_msg)
            else:
                # 已经处理过的错误，直接重新抛出
                raise
    
    def _select_template_path(self, template_path=None):
        """选择要使用的模板文件路径
        
        Args:
            template_path (str, optional): 用户上传的模板文件路径
            
        Returns:
            str: 最终使用的模板文件路径
            
        Raises:
            FileNotFoundError: 当没有可用的模板文件时
        """
        # 优先使用用户上传的模板文件
        if template_path and os.path.exists(template_path):
            return template_path
        
        # 回退到系统默认模板文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        default_template_paths = [
            os.path.join(backend_dir, 'temp', 'default', 'ppt初版.pptx'),
            os.path.join(backend_dir, 'ppt初版.pptx'),
            'ppt初版.pptx'
        ]
        
        for path in default_template_paths:
            if os.path.exists(path):
                ppt_logger.info(f"使用默认模板: {path}")
                return path
        
        # 如果都不存在，抛出异常
        error_msg = f"找不到可用的模板文件。已尝试的路径: {[template_path] + default_template_paths if template_path else default_template_paths}"
        ppt_logger.error(error_msg)
        raise FileNotFoundError(error_msg)

# 创建全局实例供其他模块导入使用
ppt_service = PPTService()