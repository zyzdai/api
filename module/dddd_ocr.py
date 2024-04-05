import ddddocr
import requests

def get_captcha(url):
    # 获取验证码图片
    img = requests.get(url).content
    # 使用ddddocr识别验证码
    ocr = ddddocr.DdddOcr()
    result = ocr.classification(img)
    return result