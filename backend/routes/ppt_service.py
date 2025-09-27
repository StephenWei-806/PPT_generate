import json
import re

from .llm_service import LLMService
from utils.ppt_utils import replace_text_in_ppt
from utils.json_utils import extract_json_from_text, validate_ppt_json

class PPTService:
    """PPT服务类，用于生成PPT内容和处理相关操作"""
    
    def generate_ppt_response(self, input_content, page_count, model, api_key) :
        """生成PPT响应内容
        
        Args:
            input_content (str): 输入内容
            page_count (int): PPT页数
            model (str): 使用的LLM模型
            api_key (str): API密钥
            
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
                yield "错误: 未收到LLM响应内容，请检查API密钥和网络连接\n"
                return
                
            print(f"[调试] 收到的完整内容: {full_content[:200]}...")
            
            # 解析JSON并生成PPT
            # 清理Markdown代码块格式
            full_content = full_content.replace('```json', '').replace('```', '').strip()
            
            
            try:
                # 尝试从文本中提取JSON
                json_str = extract_json_from_text(full_content)
                
                # 解析提取出的JSON字符串
                json_data = json.loads(json_str)
                print(f"[调试] JSON解析成功: {json_data}")
                
            except Exception as e:
                
                yield f"JSON解析失败: {str(e)}\n"
                return
            
            # 验证JSON结构是否符合PPT要求
            try:
                # 确保json_data已定义且不为None
                if json_data is None:
                    raise ValueError("JSON数据未定义或为None")
                validate_ppt_json(json_data)
                
            except Exception as e:
                print(f"[调试] JSON验证失败: {str(e)}")
                
                yield f"JSON验证失败: {str(e)}\n"
                return
            
            # 替换PPT内容
            try:
                # 确保json_data已定义且不为None
                if json_data is None:
                    raise ValueError("JSON数据未定义或为None")
                # 使用正确的模板文件路径（位于backend目录下）
                result_file = replace_text_in_ppt(json.dumps(json_data), 'ppt初版.pptx')
                yield f"PPT生成成功: {result_file}\n"
                
            except Exception as e:
                print(f"[调试] PPT生成失败: {str(e)}")
                
                # 记录异常时的json_data值
                print(f"[调试] 异常时json_data值: {json_data}")
                
                yield f"PPT生成失败: {str(e)}\n"
                return
        return generate_response

# 创建全局实例供其他模块导入使用
ppt_service = PPTService()