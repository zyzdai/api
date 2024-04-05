import os
import uuid
from module import tools
TMP_DIR = 'tmp/edge_tts'
os.makedirs(TMP_DIR, exist_ok=True)

# tts
voiceMap = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
    "yunjian": "zh-CN-YunjianNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "yunxia": "zh-CN-YunxiaNeural",
    "yunyang": "zh-CN-YunyangNeural",
    "xiaobei": "zh-CN-liaoning-XiaobeiNeural",
    "xiaoni": "zh-CN-shaanxi-XiaoniNeural",
    "hiugaai": "zh-HK-HiuGaaiNeural",
    "hiumaan": "zh-HK-HiuMaanNeural",
    "wanlung": "zh-HK-WanLungNeural",
    "hsiaochen": "zh-TW-HsiaoChenNeural",
    "hsioayu": "zh-TW-HsiaoYuNeural",
    "yunjhe": "zh-TW-YunJheNeural",
}


def getVoiceById(voiceId):
    return voiceMap.get(voiceId)

def create(text, voiceId, rate):
    file_name = f'{uuid.uuid4()}.mp3'
    mp3_path = os.path.join(TMP_DIR, file_name)
    new_text = tools.remove_html(text)
    voice = getVoiceById(voiceId)
    rate = f"+{rate}%"
    if not voice:
        return "error params"
    if not os.path.exists(mp3_path):
        # 用open创建文件 兼容mac
        open(mp3_path, 'a').close()
    script = 'edge-tts --rate=' + rate + ' --voice ' + voice + ' --text "' + new_text + '" --write-media ' + mp3_path
    os.system(script)
    return mp3_path

