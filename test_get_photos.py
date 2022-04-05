import os
import requests

url = 'https://img1.591.com.tw/house/2021/12/28/164068242952071108.png!510x400.jpg'
r = requests.get(url, stream=True)

if not os.path.exists('./photos/'):
    os.mkdir('./photos/')

image_name = 'test.jpg'

with open(f'./photos/{image_name}', 'wb') as file:
    for chuck in r.iter_content(1024):
        file.write(chuck)
