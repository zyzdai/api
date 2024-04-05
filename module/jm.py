import hashlib
import os
import uuid
import requests
from PIL import Image
TMP_DIR = 'tmp/jm'
os.makedirs(TMP_DIR, exist_ok=True)
def get_num(aid, index):
    normalCutNum = 10  # 默认切割数
    aIndex = str(aid) + str(index)  # aid 和 index
    aIndex = hashlib.md5(aIndex.encode()).hexdigest()  # MD5 加密
    aIndex = ord(aIndex[-1])  # 获取最后一位的 Unicode 码表位置
    if 268850 <= int(aid) <= 421925:
        aIndex %= 10
    elif int(aid) >= 421926:
        aIndex %= 8
    if aIndex in range(10):
        normalCutNum = 2 + 2 * aIndex
    return normalCutNum

def on_image_loaded(url):
    # aid = 421536  # 漫画id
    outfile_name = os.path.join(TMP_DIR, hashlib.md5(url.encode()).hexdigest() + '.jpg')
    if  os.path.exists(outfile_name):
        return outfile_name
    urls = url.split('/')
    aid = urls[-2]
    img_name = urls[-1]
    img_path = os.path.join(TMP_DIR, f'{uuid.uuid4()}.jpg')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(img_path, 'wb') as file:
            file.write(response.content)
        print(f"文件 {img_path} 下载成功")
    else:
        print(response.status_code,response.text)
        print("下载失败")
    img = Image.open(img_path)
    canvas = Image.new('RGB', img.size)  # 创建一个与图片大小相同的画布
    canvas.paste(img)  # 将图片粘贴到画布上
    index = img_name.split(".")[0]  # 获取图片在一组中的index，当前为00002
    cut_num = get_num(str(aid), str(index))  # 获取分割次数
    unknown = img.size[1] % cut_num  # 偏移高度，最后一张图的高度会比其他图高度要高
    for m in range(cut_num):
        cut_height = img.size[1] // cut_num  # 分割的高度
        y_coordinate = cut_height * m  # 要分割的y坐标
        end_coordinate = img.size[1] - cut_height * (m + 1) - unknown  # 要分割的图片底部y
        if m == 0:
            cut_height += unknown
        else:
            y_coordinate += unknown
        region = (0, end_coordinate, img.size[0], end_coordinate + cut_height)
        region_img = img.crop(region)
        canvas.paste(region_img, (0, y_coordinate))
    canvas.save(outfile_name)  # 保存处理后的图片
    # 删除img_path文件
    os.remove(img_path)
    return outfile_name

