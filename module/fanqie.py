import gzip
import io
from datetime import time
import hashlib
import re
import time
import base64
import json
import uuid
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def gzip_data(data):
    in_memory = io.BytesIO()
    with gzip.GzipFile(fileobj=in_memory, mode='w') as f:
        f.write(data.encode('utf-8'))
    in_memory.seek(0)
    compressed_data = in_memory.read()
    return compressed_data


def En(data, key, iv):
    if not isinstance(key, bytes):
        key = key.encode()
    if not isinstance(iv, bytes):
        iv = iv.encode()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext


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


def strToBytes(s):
    bytes_list = []
    for char in s:
        bytes_list.append(ord(char))
    return bytes_list


def generateRandomBytes(length):
    uuid_str = str(uuid.uuid4()).replace('-', '')[:length]
    return strToBytes(uuid_str)


def rHex1(num):
    hex_value = hex(int(num)).replace("0x", "").zfill(32)
    res = ""
    for i in range(32, 0, -2):
        res += hex_value[i - 2:i]
    return res


def hexDecodeToByteArray(hex_string):
    return bytes.fromhex(hex_string)


def getLoginHeaders():
    # 注册
    return "&aid=1967&app_name=novelapp&channel=0&device_id=3156012172348970&device_platform=android&device_type=7&iid=3156012172353066&os_version=0&version_code=99999"


def getKey(baseUrl):
    key = base64.b64decode("rCXGfd2POMGzeiNIgo4iLg==")
    # 在这里用 Python 的方法来生成 id
    id = generateRandomBytes(16)
    did = re.search(r"device_id=(\d+)", baseUrl).group(1)
    data = hexDecodeToByteArray(rHex1(did))
    content = base64.b64encode(bytes(id) + En(data, key, bytes(id)))
    data_json = json.dumps({"content": content.decode('utf-8')})
    url = xGorgon("https://reading.snssdk.com/reading/crypt/registerkey?" +
                  getLoginHeaders(), gzip_data(data_json))
    uri = str(url).split(",{")
    url = uri[0]
    option = json.loads(("{" + uri[1]).replace("'", "\""))
    headers = {'content-encoding': 'gzip', 'accept-encoding': 'gzip', 'X-Khronos': option['headers']['X-Khronos'],
               'X-Gorgon': option['headers']['X-Gorgon'], 'Content-Type': 'application/json',
               'User-Agent': 'com.dragon.read'}
    decoded_bytes = base64.b64decode(option['body'])
    obj = requests.post(url, headers=headers,
                        data=decoded_bytes).json()['data']
    res = base64.b64decode(obj['key'])
    iv = res[:16]
    data = res[16:]
    key = base64.b64encode(De(data, key, iv))
    obj = {"key": key.decode('utf-8'), "ver": obj['keyver']}
    return json.loads(json.dumps(obj, indent=4))


def xGorgon(url, data=None):
    params = str(url).split("?")[1]

    def md5(string):
        md5 = hashlib.md5()
        if isinstance(string, str):
            md5.update(string.encode('utf-8'))
        elif isinstance(string, bytes):
            md5.update(string)
        return md5.hexdigest()

    def getHex():
        hex_params = md5(params)
        hex_data = md5(data) if data else "0" * 32
        return hex_params + hex_data + "0" * 32

    def rStr(str):
        return str[::-1]

    def Hex(num):
        return format(num, 'x').zfill(2)

    def rHex(num):
        return int(rStr(Hex(num)), 16)

    def rBin(num):
        bin_str = format(num, 'b').zfill(8)
        return int(rStr(bin_str), 2)

    def calculate(hex_str):
        length = 0x14
        key = [0xDF, 0x77, 0xB9, 0x40, 0xB9, 0x9B, 0x84, 0x83, 0xD1, 0xB9, 0xCB, 0xD1, 0xF7, 0xC2, 0xB9, 0x85, 0xC3,
               0xD0, 0xFB, 0xC3]
        param_list = []
        for i in range(0, 9, 4):
            temp = hex_str[8 * i:8 * (i + 1)]
            for j in range(4):
                h = int(temp[2 * j:2 * (j + 1)], 16)
                param_list.append(h)
        param_list.extend([0x0, 0x6, 0xB, 0x1C])
        T = int(time.time())
        param_list.extend([(T >> 24) & 0xFF, (T >> 16) &
                          0xFF, (T >> 8) & 0xFF, T & 0xFF])

        eor_result_list = [param ^ key[i % length]
                           for i, param in enumerate(param_list)]
        for i in range(length):
            A = rHex(eor_result_list[i])
            B = eor_result_list[(i + 1) % length]
            C = A ^ B
            D = rBin(C)
            F = ((D ^ 0xFFFFFFFF) ^ length) & 0xFF
            eor_result_list[i] = F
        result = "".join([Hex(param) for param in eor_result_list])
        option = {
            "headers": {
                "X-Khronos": str(T),
                "X-Gorgon": "0404b0d30000" + result
            }
        }
        if data:
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                # 如果 data 已经是一个字节对象，直接赋值
                data_bytes = data
            encoded_data = base64.b64encode(data_bytes)
            option["body"] = encoded_data.decode('utf-8')
        return option
    return url + "," + str(calculate(getHex()))


def getContent(item_id):
    baseUrl = "https://reading.snssdk.com/reading/reader/full/v/?item_id=" + \
        item_id+getLoginHeaders()
    result = requests.get(baseUrl).json()['data']
    baseUrl = str(xGorgon(baseUrl))
    if result["content"] == "Invalid":
        result = requests.get(baseUrl).json()['data']
    json_key = getKey(baseUrl)
    ver = result["key_version"]
    if json_key == "" or ver != json_key["ver"]:
        json_key = getKey(baseUrl)
    key = json_key["key"]
    res = base64.b64decode(result["content"])
    key = base64.b64decode(key)
    iv = res[:16]
    result = De(res[16:], key, iv)
    result = result.decode('utf-8')
    return result
# print(getContent("6982736217976603143"))
