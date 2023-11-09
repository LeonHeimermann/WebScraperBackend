import requests
from bs4 import BeautifulSoup

import drawer
import normalizer


base_url = 'https://www.h-brs.de'
url_path = ''

response = requests.get(f'{base_url}/{url_path}')
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')

normalizer.normalize_tree(soup)
print(soup.prettify())

drawer.draw(soup.body)
