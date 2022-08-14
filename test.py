import requests
from tqdm import tqdm

a = 'https'
b = 'http://127.0.0.1:10809'

file = requests.get('https://files.yande.re/image/43b286e0984b40e79f3d4afaa76638c2/yande.re%20387696%20japanese_clothes%20kagura_%28onmyouji%29%20onmyouji%20thank_star.jpg', proxies={a: b}, stream=True)
file_size = int(file.headers.get('content-length', 0))

with open("FES.jpg", "wb") as f, tqdm(
    desc=f'Picture',
    total=file_size,
    unit='iB',
    unit_scale=True,
    unit_divisor=1024,
    ascii=True,
    leave=False,
) as bar:
    for data in file.iter_content(chunk_size=1024):
        size = f.write(data)
        bar.update(size)

print('test')