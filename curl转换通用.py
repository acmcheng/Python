import re
import json
import pyperclip
from urllib.parse import urlparse


def parse_curl_command(curl_command):
    """解析curl命令的各个组件"""
    result = {
        'method': 'GET',
        'url': '',
        'headers': {},
        'data': None,
    }

    # 提取URL
    url_match = re.search(r"curl '([^']*)'", curl_command)
    if url_match:
        result['url'] = url_match.group(1)
        if any(ext in result['url'].lower() for ext in ['.ico', '.png', '.jpg', '.jpeg', '.gif', '.css', '.js']):
            return None
        # 已去除根据URL判断API类型的代码

    # 提取请求方法
    if "-X 'POST'" in curl_command or "--data" in curl_command:
        result['method'] = 'POST'
    elif "-X 'OPTIONS'" in curl_command:
        return None

    # 提取headers
    headers_matches = re.finditer(r"-H '([^:]+): ([^']+)'", curl_command)
    essential_headers = {
        'accept': None,
        'accept-language': None,
        'authorization': None,
        'content-type': None,
        'origin': None,
        'referer': None
    }

    for match in headers_matches:
        key = match.group(1).lower()
        value = match.group(2)
        if key in essential_headers:
            result['headers'][key] = value

    # 提取data
    data_match = re.search(r"--data-raw '([^']*)'", curl_command)
    if data_match:
        try:
            data_str = data_match.group(1).replace('\\"', '"')
            result['data'] = json.loads(data_str)
        except json.JSONDecodeError:
            result['data'] = data_match.group(1)

    return result


def generate_python_code(curl_components):
    """生成Python代码"""
    if not curl_components:
        return ""

    code_lines = ['import requests\n']

    # 生成headers
    if curl_components['headers']:
        code_lines.append('headers = {')
        for key, value in curl_components['headers'].items():
            code_lines.append(f"    '{key}': '{value}',")
        code_lines.append('}\n')

    # 生成data
    if curl_components['data']:
        code_lines.append('json_data = {')
        if isinstance(curl_components['data'], dict):
            for key, value in sorted(curl_components['data'].items()):
                if isinstance(value, str):
                    code_lines.append(f"    '{key}': '{value}',")
                else:
                    code_lines.append(f"    '{key}': {value},")
        code_lines.append('}\n')

    # 生成请求
    request_line = f"response = requests.{curl_components['method'].lower()}('{curl_components['url']}'"
    if curl_components['headers']:
        request_line += ', headers=headers'
    if curl_components['data']:
        request_line += ', json=json_data'
    request_line += ')'
    code_lines.append(request_line)

    # 添加打印响应结果
    code_lines.append('print(response.json())')

    return '\n'.join(code_lines)


def process_curl_command(curl_command):
    """处理curl命令"""
    commands = re.split(r';(?=\s*curl)', curl_command)

    # 只处理第一个有效的请求
    for command in commands:
        if not command.strip():
            continue

        components = parse_curl_command(command.strip())
        if components and components['data']:  # 优先处理带有data的请求
            return generate_python_code(components)

    # 如果没有带data的请求，处理第一个有效请求
    for command in commands:
        if not command.strip():
            continue

        components = parse_curl_command(command.strip())
        if components:
            return generate_python_code(components)

    return ""


def convert_curl_to_python():
    """主函数：从剪贴板读取curl命令并转换为Python代码"""
    try:
        curl_command = pyperclip.paste()

        if not curl_command.strip().startswith('curl'):
            print("错误：剪贴板内容不是有效的curl命令")
            return

        python_code = process_curl_command(curl_command)

        if not python_code:
            print("没有找到有效的请求")
            return

        pyperclip.copy(python_code)

        print("转换结果:")
        print(python_code)
        print("\n代码已复制到剪贴板")

    except Exception as e:
        print(f"转换过程中发生错误: {e}")


if __name__ == "__main__":
    convert_curl_to_python()
