# 删除html标签
import requests
import random
import re
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
TMP_DIR = 'tmp'


def remove_html(string):
    regex = re.compile(r'<[^>]+>')
    return regex.sub('', string)



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
        return None


def De(ciphertext, key, iv):
    if not isinstance(key, bytes):
        key = key.encode()
    if not isinstance(iv, bytes):
        iv = iv.encode()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(decrypted_data) + unpadder.finalize()
    return data
