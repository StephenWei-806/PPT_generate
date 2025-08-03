import json
import json
def extract_json_from_text(text):
    """从文本中提取并验证JSON数据"""

    # 去除Markdown代码块标记
    text = text.replace("```json", "").replace("```", "")

    # 尝试使用json模块直接解析
    try:
        # 尝试从文本中提取并解析JSON
        # 查找JSON的开始和结束位置
        start_index = text.find("{")
        if start_index == -1:
            raise ValueError("无法找到JSON开始标记 '{'")
        
        # 尝试匹配括号对，处理嵌套JSON
        bracket_count = 1
        end_index = start_index + 1
        while end_index < len(text) and bracket_count > 0:
            if text[end_index] == '{':
                bracket_count += 1
            elif text[end_index] == '}':
                bracket_count -= 1
            end_index += 1
        
        if bracket_count > 0:
            raise ValueError("无法找到匹配的JSON结束标记 '}'")
        
        json_str = text[start_index:end_index]

        # 验证JSON是否有效
        json_data = json.loads(json_str)
        return json_str
    except json.JSONDecodeError as e:
        # 尝试修复常见问题，如多余的逗号
        try:
            # 移除末尾多余的逗号
            json_str = json_str.rstrip(',')
            json_data = json.loads(json_str)
            return json_str
        except:
            raise ValueError(f"JSON格式无效: {str(e)}")
    except Exception as e:
        raise ValueError(f"无法提取有效的JSON: {str(e)}")

# 添加一个辅助函数来验证JSON结构是否符合PPT要求
def validate_ppt_json(json_data):
    try:
        if not isinstance(json_data, dict):
            return False, "JSON必须是一个对象"
        
        # 检查必需字段
        required_fields = ['title', 'name']
        for field in required_fields:
            if field not in json_data:
                return False, f"缺少必需字段: {field}"
        
        # 检查页面结构
        page_keys = [key for key in json_data.keys() if key.startswith('title') and len(key) == 6 and key[5].isdigit()]
        if not page_keys:
            return False, "缺少页面标题字段，格式应为titleN"
        
        for page_key in page_keys:
            page_num = page_key[5]
            # 检查子标题
            for i in range(1, 4):
                sub_title_key = f"title{page_num}-{i}"
                if sub_title_key not in json_data:
                    return False, f"缺少子标题字段: {sub_title_key}"
            # 检查数据字段
            for i in range(1, 4):
                data_key = f"data{page_num}-{i}"
                if data_key not in json_data:
                    return False, f"缺少数据字段: {data_key}"
        
        return True, "JSON结构验证通过"
    except Exception as e:
        return False, f"验证过程中发生错误: {str(e)}"
