import requests
from bs4 import BeautifulSoup

url_site = 'http://tululu.org'
url_book = 'http://tululu.org/b1/'

response = requests.get(url_book)
response.raise_for_status()


soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('h1').find('a')
title_text = title_tag.text
img_src = soup.select_one('.bookimage a img')
src_img = img_src['src']
print(title_text)
print(url_site+src_img)

