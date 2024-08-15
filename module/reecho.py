
import requests
import json

def get_reecho(text, voiceId="ce4e397d-2bdb-410f-ab6b-7306f2e41f9d", mode="balance"):
    headers = {
        "content-type": "application/json",
        "referer": "https://dash.reecho.cn/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    url = "https://v1.reecho.cn/api/welcome/generate"
    data = {
        "voiceId": voiceId,
        "text": text,
        "mode": mode
    }
    data = json.dumps(data, separators=(',', ':'))
    response = requests.post(url, headers=headers, data=data)
    res = response.json()
    if res['status'] == 200:
        mp3url = res['data']['url']
        response = requests.get(mp3url)
        return response.content
    else:
        return None


get_reecho('你好，我是小智，很高兴见到你')