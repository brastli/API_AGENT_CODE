from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_code(text):
    """去除 Markdown 格式，只保留纯代码"""
    text = text.replace("```python", "").replace("```", "")
    return text.strip()

def generate_test_code(api_info):
    prompt = f"""
    你需要为一个 API 编写 Python 测试脚本。
    API URL: {api_info['url']}
    Method: {api_info['method']}
    Payload 模板: {api_info.get('payload_template', 'None')}

    要求：
    1. 使用 `requests` 库。
    2. 必须捕获异常。
    3. 必须在最后打印: "STATUS_CODE: <codeData>, RESPONSE: <bodyData>" 格式的输出，以便我后续解析。
    4. 不要任何解释性文字，只返回 Python 代码。
    """
    
    response = client.chat.completions.create(
        model="gpt-4o", # 或 gpt-3.5-turbo
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return clean_code(response.choices[0].message.content)

def fix_code(old_code, error_msg):
    prompt = f"""
    这段代码运行报错了，请修复它。
    
    [错误信息]:
    {error_msg}

    [源代码]:
    {old_code}

    要求：只返回修复后的 Python 代码。
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return clean_code(response.choices[0].message.content)

def evaluate_output(api_info, execution_output):
    prompt = f"""
    请根据 API 测试的运行输出来判断测试是否通过。
    
    API目标: {api_info['url']}
    运行输出: {execution_output}

    要求：
    1. 分析状态码和返回内容是否合理。
    2. 返回格式必须是: "PASS: <原因>" 或 "FAIL: <原因>"
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content