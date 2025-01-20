import re
import json
import pyperclip


def parse_curl(curl_command):
    # 提取 URL
    url_match = re.search(r"curl\s+'([^']*)'|curl\s+\"([^\"]*)\"|curl\s+(\S+)", curl_command)
    if not url_match:
        raise ValueError("未找到有效的 URL")
    url = url_match.group(1) or url_match.group(2) or url_match.group(3)

    # 提取头部信息
    headers = {}
    header_matches = re.findall(r"-H\s+'([^:]+):\s*(.*?)'|-H\s+\"([^:]+):\s*(.*?)\"|-H\s+([^:]+):\s*(\S+)",
                                curl_command)
    for match in header_matches:
        key = match[0] or match[2] or match[4]
        value = match[1] or match[3] or match[5]
        headers[key.strip()] = value.strip()

    # 提取数据
    data_match = re.search(r"--data-raw\s+'(.*)'|--data-raw\s+\"(.*)\"|--data-raw\s+(\S+)", curl_command)
    data = None
    if data_match:
        raw_data = data_match.group(1) or data_match.group(2) or data_match.group(3)
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            data = raw_data.strip("'\"")

    # 判断请求方法
    method = "POST" if "--data-raw" in curl_command else "GET"

    return url, headers, data, method


def generate_python_code(url, headers, data, method):
    # 生成 Python 请求代码
    code = f"""import requests

url = '{url}'
headers = {{
"""
    for key, value in headers.items():
        code += f"    '{key}': '{value}',\n"
    code += "}\n"

    if data:
        code += f"data = {json.dumps(data, indent=4)}\n"
        code += "response = requests.post(url, headers=headers, json=data)\n"
    else:
        code += "response = requests.get(url, headers=headers)\n"

    code += "print(response.text)\n"
    return code


def main():
    try:
        # 从剪贴板获取内容
        curl_command = pyperclip.paste().strip()

        # 移除多行换行符及反斜杠，拼接为单行
        curl_command = " ".join(curl_command.splitlines()).replace("\\", "")

        # 解析 curl 命令
        url, headers, data, method = parse_curl(curl_command)

        # 生成 Python 代码
        python_code = generate_python_code(url, headers, data, method)

        # 自动复制到剪贴板
        pyperclip.copy(python_code)

        print("\n生成的 Python 代码如下 (已复制到剪贴板):\n")
        print(python_code)
    except Exception as e:
        print(f"解析 curl 命令时出错: {e}")


if __name__ == "__main__":
    main()
