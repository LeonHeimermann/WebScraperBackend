import re

import bs4


class Counter:
    def __init__(self, initial_value=0):
        self.value = initial_value

    def increment(self):
        self.value += 1


class ProgressIndicator:
    def __init__(self, initial_value=0):
        self.progress: float = initial_value
        self.started: bool = False
        self.finished: bool = False

    def to_dict(self):
        return {
            'progress': self.progress,
            'started': self.started,
            'finished': self.finished
        }


def remove_branch(start_element: bs4.element.Tag):
    if start_element.name is None:
        return
    current_element = start_element
    while len(current_element.parent.find_all(recursive=False)) == 1:
        current_element = current_element.parent
    current_element.decompose()


def has_unwrapped_content(element: bs4.element.Tag):
    return len(get_unwrapped_strings(element)) > 0 and not is_element_content_tag(element)


def is_element_content_tag(element: bs4.element.Tag):
    return element.name in state['content_tags']


def get_unwrapped_strings(current_element: bs4.element.Tag):
    unwrapped_strings = current_element.find_all(text=True, recursive=False)
    return list(filter(lambda string: string != "", map(lambda string: string.strip(), unwrapped_strings)))


def find_all_structures(start_element: bs4.element.Tag):
    elements = start_element.find_all(
        lambda tag: len(tag.find_previous_siblings()) == 0 and is_alternating_element(tag) and len(tag.parent.find_all(recursive=False)) >= 3)
    return list(map(lambda element: element.parent, elements))


def is_alternating_element(start_element: bs4.element.Tag):
    children = start_element.find_all(recursive=False)
    return len(children) == 1 and len(children[0].find_all(recursive=False)) == 0


def is_valid_relative_path(path):
    return path.startswith("/") and not bool(re.search(r"\.[a-zA-Z0-9]+$", path))


def is_valid_absolute_url(base_url, url):
    return base_url in url and bool(re.match(r"^(https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?$", url))


def create_identifier(base_url, url_path, max_depth, max_searched_pages):
    return f"{base_url}_{url_path}_{max_depth}_{max_searched_pages}"


def extract_identifier_data(data):
    base_url = data.get('base_url')
    url_path = data.get('url_path')
    max_depth = int(data.get('max_depth'))
    max_searched_pages = int(data.get('max_searched_pages'))
    return base_url, url_path, max_depth, max_searched_pages


def normalize_url(url: str, base_url: str):
    return url.replace(base_url, "") if base_url in url else url


state = {
    "normalize_text_tags": ['br', 'em', 'strong', 'i', 'b'],
    "unwanted_tags": ['img', 'svg', 'picture', 'script', 'source', 'iframe', 'style', 'link', 'sup'],
    "content_tags": ['p', 'a'] + [f'h{i + 1}' for i in range(10)]
}
