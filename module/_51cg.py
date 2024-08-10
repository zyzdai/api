import requests
from module import tools
import base64
def decrypt_image(url,key,iv):
    url = base64.b64decode(url).decode('utf-8')
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    res = response.content
    # media_key = b'f5d965df75336270'
    # media_iv = b'97b60394abc2fbe1'
    decrypted_bytes = tools.De(res, key.encode(), iv.encode())
    return decrypted_bytes
