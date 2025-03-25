import requests
import json
import pyperclip

url = "https://serverapi.trumanwl.com/api/curl-convert"

headers = {
    "sec-ch-ua-platform": '"Windows"',
    "Referer": "https://trumanwl.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "Content-Type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "Origin": "https://trumanwl.com"
}

# 从剪贴板获取最新的curl数据
clipboard_curl = pyperclip.paste()

data = {
    "language": "python",
    "content": clipboard_curl
}

# 发送 POST 请求
response = requests.post(url, headers=headers, json=data)

try:
    # 解析响应的 JSON 数据
    response_data = response.json()
    # 获取 content 字段
    content = response_data["content"]
    # 删除注释代码
    lines = content.splitlines()
    non_comment_lines = []
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line.startswith('#'):
            non_comment_lines.append(line)
    content_without_comments = '\n'.join(non_comment_lines)
    # 构建要打印和复制的内容
    # output = f"{content_without_comments}\nprint(response.text)"

    output = f"import json\n{content_without_comments}\nparsed_data = json.loads(response.text)\nformatted_json = json.dumps(parsed_data, indent=4, ensure_ascii=False)\nprint(formatted_json)"

    # 打印内容
    print(output)
    # 将结果复制到剪贴板
    pyperclip.copy(output)
except json.JSONDecodeError:
    print("无法解析响应的JSON数据。")
except KeyError:
    print("响应中没有 'content' 字段。")
