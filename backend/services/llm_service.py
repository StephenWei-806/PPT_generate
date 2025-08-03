import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
import json
import os

# 加载环境变量
load_dotenv()

def call_llm_api(prompt, num, model=None):
    # 使用默认模型（从环境变量获取）
    model = model or os.getenv("DEFAULT_MODEL", "tongyi")
    try:
        # 构建提示词
        beg = (
            f"请严格按照以下JSON格式生成{num}页PPT内容，总结《{prompt}》。"
            "输出必须完全符合以下格式要求："
            "1. 顶层包含'title'（主标题）和'name'（机构名称）字段，为字符串类型"
            f"2. 每个'titleN'（N=1到{num}）代表一个独立页面，必须包含3个子标题（titleN-1/titleN-2/titleN-3）和3个数据字段（dataN-1/dataN-2/dataN-3）"
            "3. 字段命名必须严格遵循'titleN-M'和'dataN-M'的层级规则（如title4-1、data4-1），N代表页码(1开始)，M代表位置(1-3)"
            "4. 每个页面需覆盖全新主题，内容需专业且无重复，各页面逻辑连贯形成完整报告"
            "5. 每个data字段必须使用段落式描述（每段至少3行），单页总字数控制在2000-2500字"
            "6. 输出仅包含上述字段，禁止添加任何额外说明或解释，JSON生成完毕立刻结束"
            "7. 严禁虚构内容，只允许总结输入文档内容。若内容不足，可减少1-3页PPT并在最后一页添加'内容摘要'说明"
            "8. 必须生成完整可解析的JSON，包含所有必要括号和引号，格式参考：\n"
            "  {\n" +
            "    \"title\": \"文档总结报告\",\n" +
            "    \"name\": \"某机构\",\n" +
            "    \"title1\": \"核心概念与背景介绍\",\n" +
            "    \"title1-1\": \"定义与内涵\",\n" +
            "    \"title1-2\": \"发展历程\",\n" +
            "    \"title1-3\": \"研究意义\",\n" +
            "    \"data1-1\": \"详细段落内容...（至少3行）\",\n" +
            "    \"data1-2\": \"详细段落内容...（至少3行）\",\n" +
            "    \"data1-3\": \"详细段落内容...（至少3行）\"\n" +
            "  }"
            "9. 生成前请验证JSON格式完整性，确保无语法错误"
        )
        
        # API请求参数
        # 根据选择的模型配置OpenAI客户端
        if model == "tongyi":
            client = OpenAI(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            model_name = "qwen-plus"
        elif model == "deepseek":
            client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
            model_name = "deepseek-chat"
        else:
            raise ValueError(f"不支持的模型: {model}")

        # 构造消息
        messages = [
            {"role": "system", "content": "你是一个PPT制作专家，擅长将文本内容转换为结构化的PPT大纲。"},
            {"role": "user", "content": f"{beg}"}
        ]

        # 发送请求
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=8192
        )
        
        # 处理流式响应
        full_response = ""
        print("开始接收LLM响应...")
        for chunk in response:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    print(f"收到LLM响应片段: {content}")
                    yield content
        print(f"LLM响应完成，完整内容: {full_response}")
    except Exception as e:
        # 捕获OpenAI相关异常
        print(f"LLM API调用失败: {str(e)}")
        print(f"请求失败: {e}")
    finally:
        pass