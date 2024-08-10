import requests
from module import tools
def decrypt_image(url,key,iv):
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    res = response.content
    media_key = key.encode()
    media_iv = iv.encode()
    decrypted_bytes = tools.De(res, media_key, media_iv)
    return decrypted_bytes

# decrypt_image("", "my2ecret782ecret", "my2ecret782ecret")
