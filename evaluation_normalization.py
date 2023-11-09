import requests
from bs4 import BeautifulSoup

import normalizer
import utils


def get_evaluation_score(soup: BeautifulSoup):
    leaf_elements = soup.body.find_all(lambda tag: len(utils.get_unwrapped_strings(tag)) > 0)
    normalizer.normalize_tree(soup)
    soup_str = str(soup)
    found_counter = 0
    not_found_counter = 0
    for leaf_element in leaf_elements:
        unwrapped_strings = utils.get_unwrapped_strings(leaf_element)
        for unwrapped_string in unwrapped_strings:
            if unwrapped_string in soup_str:
                found_counter += 1
            else:
                not_found_counter += 1

    if found_counter + not_found_counter == 0:
        return None

    return not_found_counter / (found_counter + not_found_counter)


base_url = 'https://www.h-brs.de'
url_path = ''

found_links = {url_path}
url_list = [(url_path, 0)]
index = 0
score = 0.0
score_counter = 0

while True:
    if index >= 10000 or index >= len(url_list):
        break
    if index % 100 == 0:
        print(index)

    current_url_path, depth = url_list[index]

    response = requests.get(base_url + current_url_path)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    if soup is not None and soup.body is not None:
        score_tmp = get_evaluation_score(soup)
        if score_tmp is not None:
            score += score_tmp
            score_counter += 1
        new_links = soup.find_all('a')
        for new_link_tmp in new_links:
            if new_link_tmp.get('href') is not None:
                new_link = utils.normalize_url(new_link_tmp.get('href'), base_url)
                if new_link is not None and new_link not in found_links:
                    found_links.add(new_link)
                    if utils.is_valid_relative_path(new_link):
                        url_list.append((new_link, depth + 1))

    index += 1

print("---------------")
print(index)
print(score / score_counter)
