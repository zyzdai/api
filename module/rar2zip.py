import shutil
from datetime import time
import requests
from urllib.parse import quote
import rarfile
import os
import uuid
TMP_DIR = 'tmp/rar2zip'
os.makedirs(TMP_DIR, exist_ok=True)


def rar2zip(rar_file):
    rar = rarfile.RarFile(rar_file)
    # 取rar_file文件名
    file_name = os.path.basename(rar_file).split('.')[0]
    work_dir = os.path.join(TMP_DIR,file_name)
    rar.extractall(work_dir)
    rar.close()
    zip_file = os.path.join(TMP_DIR, f'{uuid.uuid4()}')
    shutil.make_archive(zip_file, 'zip',os.path.join(os.path.dirname(rar_file), file_name))
    shutil.rmtree(work_dir)
    os.remove(rar_file)
    # 清除超过1天的zip文件
    clear_zip_file()
    return zip_file+".zip"


def clear_zip_file(sec=120):
    zip_file_list = os.listdir(os.getcwd())
    for file in zip_file_list:
        if file.endswith('.zip') or file.endswith('mp3') or file.endswith('jpg'):
            zip_file_time = os.path.getmtime(file)
            if (time.time() - zip_file_time) > sec:
                os.remove(file)


def r2z(url):
    filePath = os.path.join(TMP_DIR, f"{uuid.uuid4()}.rar")
    os.makedirs(os.path.dirname(filePath), exist_ok=True)
    url = quote(url, safe=':/')
    # 下载文件
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers,stream=True)
    # 检查请求是否成功
    if response.status_code == 200:
        # 打开文件并写入内容
        with open(filePath, 'wb') as f:
            f.write(response.content)
        print("文件下载完成:", filePath)
    else:
        print("文件下载失败")
    zipName = rar2zip(filePath)
    return zipName


