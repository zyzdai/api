import os
import uuid
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
TMP_DIR = 'tmp/51cg'
os.makedirs(TMP_DIR, exist_ok=True)


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


def decrypt_image(url):
    out_path = os.path.join(TMP_DIR, f'{uuid.uuid4()}.jpg')
    response = requests.get(url)
    print(response.status_code)
    res = response.content
    media_key = b'f5d965df75336270'
    media_iv = b'97b60394abc2fbe1'
    decrypted_bytes = De(res, media_key, media_iv)
    with open(out_path, 'wb') as f:
        f.write(decrypted_bytes)
    return out_path

# decrypt_image('https://pic.qhvxxpp.cn/upload/xiao/20240329/2024032911440758410.jpeg')
