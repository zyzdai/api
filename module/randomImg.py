import random

import requests


def img():
    skip = random.randint(1, 20)
    url = f'http://service.picasso.adesk.com/v1/vertical/category/4e4d610cdf714d2966000000/vertical?limit=20&skip={skip}&adult=false&first=1&order=hot'
    resource = requests.get(url)
    if resource.status_code == 200:
        arr = resource.json()['res']['vertical']
        # 随机选择
        img = random.choice(arr)
        return img['wp']
    return ''