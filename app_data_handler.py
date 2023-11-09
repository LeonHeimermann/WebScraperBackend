from concurrent.futures import ThreadPoolExecutor
from cachetools import TTLCache

import utils
import web_parser


def create_web_page_graph(base_url: str, url_path: str, max_depth: int, max_searched_pages: int):
    identifier = utils.create_identifier(base_url, url_path, max_depth, max_searched_pages)
    if identifier in graph_cache:
        return
    progress_indicators[identifier] = utils.ProgressIndicator()
    executor.submit(web_parser.create_web_page_graph_handler, base_url, url_path, max_depth, max_searched_pages,
                    progress_indicators[identifier], graph_cache)


def get_progress(base_url: str, url_path: str, max_depth: int, max_searched_pages: int) -> utils.ProgressIndicator:
    identifier = utils.create_identifier(base_url, url_path, max_depth, max_searched_pages)
    if identifier not in progress_indicators:
        return utils.ProgressIndicator()
    return progress_indicators[identifier]


def get_main_data(base_url: str, url_path: str, max_depth: int, max_searched_pages: int):
    identifier = utils.create_identifier(base_url, url_path, max_depth, max_searched_pages)
    if identifier not in graph_cache:
        return None
    web_page_graph_handler = graph_cache[identifier][0]
    return web_parser.extract_main_data(web_page_graph_handler)


def search_keywords(base_url: str, url_path: str, max_depth: int, max_searched_pages: int, keyword_list: [str]):
    identifier = utils.create_identifier(base_url, url_path, max_depth, max_searched_pages)
    if identifier not in graph_cache:
        return None
    web_page_graph_handler = graph_cache[identifier][0]
    return web_parser.search_keyword_list(web_page_graph_handler, keyword_list)


def get_normalized_page(base_url: str, url_path: str, max_depth: int, max_searched_pages: int, requested_page_url: str):
    identifier = utils.create_identifier(base_url, url_path, max_depth, max_searched_pages)
    print(requested_page_url)
    return str(graph_cache[identifier][1][requested_page_url])


executor = ThreadPoolExecutor(max_workers=4)
graph_cache = TTLCache(maxsize=1000, ttl=3600)
progress_indicators = {}
