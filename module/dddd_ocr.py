import base64

import ddddocr
import requests

def get_captcha(url):
    # 获取验证码图片
    img = requests.get(url).content
    with open('captcha.png', 'wb') as f:
        f.write(img)
    # 使用ddddocr识别验证码
    ocr = ddddocr.DdddOcr()
    result = ocr.classification(img)
    print(result)
    return result


def get_captcha_fromB64(imgB64):
    img = base64.b64decode(imgB64)
    # 使用ddddocr识别验证码
    ocr = ddddocr.DdddOcr()
    result = ocr.classification(img)
    print(result)
    return result