import hashlib
import os
import subprocess
import uuid
from datetime import datetime, timedelta
import random
import requests
from module import dddd_ocr, tools
TMP_DIR = 'tmp/qqttson'
os.makedirs(TMP_DIR, exist_ok=True)


def getXch():
    current_time = (datetime.now() - timedelta(hours=8)).isoformat()[:13]
    timestamped_string = "alex" + current_time
    hashed_string = hashlib.md5(timestamped_string.encode()).hexdigest()
    return hashed_string


def generate_random_ip():
    ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    return ip


def get_captcha():
    # 取随机数7694230510251072
    t = tools.generate_random_number()
    url = f"https://u95167-bd74-2aef8085.westx.seetacloud.com:8443/flashsummary/captcha?0.{t}"
    code = dddd_ocr.get_captcha(url)
    return code


def create(voice_id, speed_factor, text, pitch_factor):
    xch = getXch()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://www.ttson.cn",
        "Pragma": "no-cache",
        "Referer": "https://www.ttson.cn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "X-Client-header": xch,
        "X-checkout-Header": "_checkout",
        "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\""
    }
    url = "https://u95167-bd74-2aef8085.westx.seetacloud.com:8443/flashsummary/tts?"
    if "." in speed_factor:
        speed_factor = float(speed_factor)
    else:
        speed_factor = int(speed_factor)
    # 重试3次
    i = 0
    while True:
        try:
            code = get_captcha()
            data = {"voice_id": int(voice_id), "to_lang": "ZH", "format": "mp3", "speed_factor": speed_factor,
                    "pitch_factor": int(pitch_factor), "volume_change_dB": 0, "emotion": 0, "text": tools.remove_html(text), "code": code}
            response = requests.post(url, headers=headers, json=data)
            jsondata = response.json()
            if jsondata["code"] == 200:
                i = 0
                break
        except Exception as e:
            print(f"第{i}次请求失败，正在重试...")
            i = i + 1
            if i > 3:
                break
    url = f'{jsondata["url"]}:{jsondata["port"]}/flashsummary/retrieveFileData?stream=True&voice_audio_path={jsondata["voice_path"]}'
    return url


def convert_to_wav(url):
    print(f"正在下载音频文件，请稍等..."+url)
    file_name = f'{uuid.uuid4()}.wav'
    wav_path = os.path.join(TMP_DIR, file_name)
    with open(wav_path, 'wb') as f:
        f.write(requests.get(url).content)

    file_output = wav_path + '.wav'
    try:
        # Convert to WAV
        convert_command = f'ffmpeg -y -i "{wav_path}" -acodec pcm_s16le -f s16le -ac 1 -ar 24000 "{file_output}" -loglevel error'
        convert_process = subprocess.run(
            convert_command, shell=True, capture_output=True, text=True)
        if convert_process.returncode != 0:
            return f'An error occurred while converting {wav_path} to .wav. Details: {convert_process.stderr.strip()}'

        # Get sample rate
        probe_command = f'ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 "{wav_path}"'
        probe_process = subprocess.run(
            probe_command, shell=True, capture_output=True, text=True)
        if probe_process.returncode != 0:
            return f'An error occurred while obtaining the sample rate. Details: {probe_process.stderr.strip()}'
        # sample_rate = probe_process.stdout.strip()

        return file_output
    except Exception as e:
        return f'An unknown error occurred. Details: {str(e)}'
