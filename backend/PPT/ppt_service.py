import json
import re
import os

from .llm_service import LLMService
from utils.ppt_utils import replace_text_in_ppt
from utils.json_utils import extract_json_from_text, validate_ppt_json
from utils.logger import ppt_logger

class PPTService:
    """PPT服务类，用于生成PPT内容和处理相关操作"""
    
    def generate_ppt_response(self, input_content, page_count, model, api_key, template_path=None):
        """生成PPT响应内容
        
        Args:
            input_content (str): 输入内容
            page_count (int): PPT页数
            model (str): 使用的LLM模型
            api_key (str): API密钥
            template_path (str, optional): 模板文件路径
            
        return:
            function: 流式响应
        """
        json_data = None  # 在外部函数也初始化变量
        def generate_response():
            nonlocal json_data  # 使用nonlocal关键字访问外部函数的变量
            full_content = ""
            json_data = None  # 在函数最开始再次初始化变量
            
            # 调用LLM服务生成内容
            # 直接使用用户输入内容作为提示词
            prompt = input_content
            # 调用LLM服务生成内容，传入API密钥
            for chunk in LLMService().call_llm_api(prompt, page_count, model=model, api_key=api_key):
                # 检查是否是错误信息
                if chunk.startswith("ERROR:"):
                    yield f"错误: {chunk[6:]}建议检查API密钥和网络连接\n"
                    return
                
                # 移除所有'data: '前缀，包括可能的空格和重复实例
                clean_chunk = re.sub(r'^(data:\s*)+', '', chunk.strip(), flags=re.MULTILINE)
                full_content += clean_chunk
                yield clean_chunk
            
            # 检查是否收到了有效内容
            if not full_content.strip():
                error_msg = "未收到LLM响应内容，请检查API密钥和网络连接"
                ppt_logger.error(f"LLM响应异常: {error_msg}")
                yield f"错误: {error_msg}\n"
                return
                
            ppt_logger.debug(f"收到的完整内容: {full_content[:200]}...")
            
            # 解析JSON并生成PPT
            # 清理Markdown代码块格式
            full_content = full_content.replace('```json', '').replace('```', '').strip()
            
            
            try:
                # 尝试从文本中提取JSON
                json_str = extract_json_from_text(full_content)
                
                # 解析提取出的JSON字符串
                json_data = json.loads(json_str)
                ppt_logger.info(f"JSON解析成功 - 包含键: {list(json_data.keys())}")
                
            except Exception as e:
                error_msg = f"JSON解析失败: {str(e)}"
                ppt_logger.error(error_msg)
                yield f"{error_msg}\n"
                return
            
            # 验证JSON结构是否符合PPT要求
            try:
                # 确保json_data已定义且不为None
                if json_data is None:
                    raise ValueError("JSON数据未定义或为None")
                validate_ppt_json(json_data)
                ppt_logger.info("JSON结构验证通过")
                
            except Exception as e:
                error_msg = f"JSON验证失败: {str(e)}"
                ppt_logger.error(error_msg)
                yield f"{error_msg}\n"
                return
            
            # 替换PPT内容
            try:
                # 确保json_data已定义且不为None
                if json_data is None:
                    raise ValueError("JSON数据未定义或为None")
                
                # 选择模板文件路径
                selected_template = self._select_template_path(template_path)
                ppt_logger.info(f"使用模板文件: {selected_template}")
                
                # 生成PPT
                result_file = replace_text_in_ppt(json.dumps(json_data), selected_template)
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'success', 
                    selected_template, result_file
                )
                yield f"PPT生成成功: {result_file}\n"
                
            except Exception as e:
                error_msg = f"PPT生成失败: {str(e)}"
                ppt_logger.log_ppt_generation(
                    input_content, page_count, model, 'failed', 
                    template_path, None, str(e)
                )
                
                # 记录异常时的json_data值
                ppt_logger.debug(f"异常时json_data值: {json_data}")
                
                yield f"{error_msg}\n"
                return
        return generate_response
    
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