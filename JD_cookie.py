#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pyperclip
import asyncio
import requests
import time
from pyppeteer import launch

# QingLong面板配置
QL_HOST = "http://localhost:5700"  # 青龙面板地址
QL_USERNAME = "chengming"  # 青龙面板用户名
QL_PASSWORD = "19960902"  # 青龙面板密码
QL_ENV_NAME = "JD_COOKIE"  # 环境变量名称

def get_ql_token():
    """获取青龙面板的token"""
    try:
        # 获取当前时间戳
        timestamp = int(time.time() * 1000)
        login_url = f"{QL_HOST}/api/user/login?t={timestamp}"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:5700',
            'Pragma': 'no-cache',
            'Referer': 'http://localhost:5700/login',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'canary': '111',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        login_data = {
            "username": QL_USERNAME,
            "password": QL_PASSWORD
        }
        
        response = requests.post(login_url, headers=headers, json=login_data)
        
        if response.status_code == 200:
            token = response.json().get("data", {}).get("token")
            if token:
                return token
            print("登录成功但未获取到token")
        else:
            print(f"登录失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
        return None
    except Exception as e:
        print(f"获取青龙面板token失败: {e}")
        return None

def add_ql_env(cookie):
    """添加环境变量到青龙面板"""
    try:
        token = get_ql_token()
        if not token:
            print("无法获取青龙面板token，请检查配置")
            return False

        # 获取当前时间戳
        timestamp = int(time.time() * 1000)
        url = f"{QL_HOST}/api/envs?t={timestamp}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "http://localhost:5700",
            "Referer": "http://localhost:5700/env",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }
        
        data = {
            "name": QL_ENV_NAME,
            "value": cookie,
            "remarks": "京东Cookie"
        }
        
        # 先检查是否存在同名环境变量
        check_url = f"{QL_HOST}/api/envs?searchValue={QL_ENV_NAME}&t={timestamp}"
        check_response = requests.get(check_url, headers=headers)
        if check_response.status_code == 200:
            envs = check_response.json().get("data", [])
            if envs:
                # 如果存在，则更新
                env_id = envs[0]["id"]
                update_url = f"{QL_HOST}/api/envs?t={timestamp}"
                update_data = {
                    "name": QL_ENV_NAME,
                    "value": cookie,
                    "remarks": "京东Cookie",
                    "id": env_id
                }
                response = requests.put(update_url, headers=headers, json=update_data)
            else:
                # 如果不存在，则创建
                response = requests.post(url, headers=headers, json=data)
        else:
            print(f"检查环境变量失败: {check_response.text}")
            # 如果检查失败，尝试直接创建
            response = requests.post(url, headers=headers, json=data)

        if response.status_code in [200, 201]:
            print("成功添加/更新Cookie到青龙面板环境变量")
            return True
        else:
            print(f"添加环境变量失败: {response.text}")
            return False
    except Exception as e:
        print(f"添加环境变量时发生错误: {e}")
        return False

def find_cookie(cookies_str):
    """提取pt_key和pt_pin
    """
    pt_pin = ''
    pt_key = ''
    for item in cookies_str.split('; '):
        if 'pt_pin=' in item:
            pt_pin = item
        elif 'pt_key=' in item:
            pt_key = item

    if pt_pin and pt_key:
        jd_cookie = pt_pin + ';' + pt_key + ';'
        pyperclip.copy(jd_cookie)  # 拷贝JDcookie到剪切板
        print("Cookie:", jd_cookie)
        print("已拷贝Cookie到剪切板、直接黏贴即可。")
        
        # 添加到青龙面板
        if QL_USERNAME and QL_PASSWORD:
            add_ql_env(jd_cookie)
        else:
            print("未配置青龙面板信息，跳过添加到环境变量")
    else:
        print("未能成功提取 pt_pin 和 pt_key.")
    # os.system('pause') # 在脚本环境中，pause可能不是最佳选择，可以考虑input提示
    input("按 Enter键 退出...")


async def main():
    """使用pyppeteer库来登录京东、并获取cookie
    """
    browser = None
    try:
        browser = await launch(headless=False, dumpio=True,
                               args=['--no-sandbox', '--window-size=1000,800', '--disable-infobars'])
        context = await browser.createIncognitoBrowserContext()  # 隐身模式

        # 关闭默认打开的第一个标签页
        pages = await browser.pages()
        if pages and len(pages) > 0:
            if len(pages) > 1 or (pages[0].url == 'about:blank' and not await context.pages()):
                 await pages[0].close()

        page = await context.newPage()
        await page.setViewport({'width': 1000, 'height': 800})
        print("正在导航到京东登录页面...")
        await page.goto('https://my.m.jd.com/index.html?sceneval=2&sourceType=smb',
                        {'timeout': 60000})

        print("等待页面加载和登录状态确认...")
        # 等待用户头像元素出现，表示已登录
        try:
            await page.waitForXPath('//*[@id="myHeader"]', timeout=60000)
            print("检测到登录状态，正在获取Cookie...")
            
            # 添加短暂延迟确保cookie已更新
            await asyncio.sleep(20)
            
            # 获取并验证cookie
            max_retries = 3
            for attempt in range(max_retries):
                cookies_list = await page.cookies()
                print(f"尝试 {attempt + 1}/{max_retries} 获取Cookie...")
                
                cookies_temp = []
                for i in cookies_list:
                    cookies_temp.append('{}={}'.format(i["name"], i["value"]))
                cookies_str = '; '.join(cookies_temp)
                
                # 验证是否获取到有效的cookie
                if 'pt_key=' in cookies_str and 'pt_pin=' in cookies_str:
                    print("成功获取到新的Cookie!")
                    find_cookie(cookies_str)
                    break
                else:
                    print("Cookie不完整，等待5秒后重试...")
                    await asyncio.sleep(5)
            
            if attempt == max_retries - 1 and ('pt_key=' not in cookies_str or 'pt_pin=' not in cookies_str):
                print("警告：未能获取到完整的Cookie，请重新运行程序。")

        except Exception as e:
            print(f"等待登录超时或发生错误: {e}")
            print("请确保完成扫码登录，然后重新运行程序。")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if browser:
            print("正在关闭浏览器...")
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e) == "asyncio.run() cannot be called from a running event loop":
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            raise