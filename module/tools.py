# 删除html标签
import requests
import os
import random
import re
import time
import base64
TMP_DIR = 'tmp'
# 删除html标签


def remove_html(string):
    regex = re.compile(r'<[^>]+>')
    return regex.sub('', string)

# 删除tmp目录过期的文件


def clearTmpFiles(sec=120):
    files = os.listdir(os.path.join(os.getcwd(), 'tmp'))
    for file in files:
        if file.endswith('mp3') or file.endswith('wav'):
            zip_file_time = os.path.getmtime(file)
            if (time.time() - zip_file_time) > sec:
                os.remove(file)


def clean_tmp_directory():
    while True:
        print("Clearing tmp directory...")
        # 清理逻辑，这里只是一个示例，你可以根据实际需求修改
        for filename in os.listdir(TMP_DIR):

            file_path = os.path.join(TMP_DIR, filename)
            if os.path.isfile(file_path):
                file_mtime = os.path.getmtime(file_path)
                if time.time() - file_mtime > 360:  # 假设超过6分钟的文件为过期文件
                    os.remove(file_path)
                    print(f"Deleted expired file: {file_path}")
            else:
                # 进入子目录
                for subfilename in os.listdir(file_path):
                    print(subfilename)
                    subfile_path = os.path.join(file_path, subfilename)
                    if os.path.isfile(subfile_path):
                        file_mtime = os.path.getmtime(subfile_path)
                        if time.time() - file_mtime > 360:
                            os.remove(subfile_path)
                            print(f"Deleted expired file: {subfile_path}")

        # 每隔一段时间执行一次清理操作，这里设定为每小时执行一次
        time.sleep(400)


# 检测参数是否为空
def isEmpty(params):
    for param in params:
        if param is None or param == '':
            return True
    return False

# 取随机数


def generate_random_number(digit=16):
    # 计算最小值和最大值
    min_value = 10 ** (digit - 1)
    max_value = (10 ** digit) - 1
    # 生成随机数
    random_number = random.randint(min_value, max_value)
    return random_number


def get_m3u8(url):
    url = base64.b64decode(url).decode('utf-8')
    headers = {
        "Referer": "http://www.guangbomi.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, verify=False)
    html = response.text
    reg = 'iframe.*?src="(.+?)"'
    m = re.search(reg, html)
    if m:
        url = m.group(1)
        # 禁止重定向
        response = requests.get(url, headers=headers,
                                allow_redirects=False, verify=False)
        location = response.headers['location']
        # 匹配出完整url
        reg = 'id=(.+?)$'
        m = re.search(reg, location)
        if m:
            url = m.group(1)
            return url
        return location
    else:
        return "服务器开小差啦"
