import normalizer
import utils
from web_page_graph_handler import WebPageGraphHandler
import web_page_data_processor
from web_page_loader import WebPageLoader
from cachetools import TTLCache


def create_web_page_graph_handler(base_url: str, url_path: str, max_depth: int, max_searched_pages: int,
                                  progress_indicator: utils.ProgressIndicator, graph_cache: TTLCache):
    identifier = utils.create_identifier(base_url, url_path, max_depth, max_searched_pages)
    web_page_loader = WebPageLoader(identifier, base_url)
    web_page_loader.add_url(url_path)

    found_links = {url_path}
    url_list = [(url_path, 0)]
    index = 0
    web_page_graph_handler = WebPageGraphHandler()
    normalized_pages = {}
    progress_indicator.started = True

    while index < len(url_list) and index < max_searched_pages:
        current_url_path, depth = url_list[index]
        if depth > max_depth:
            break

        soup = web_page_loader.get_url(current_url_path)
        if soup is not None and soup.body is not None:
            normalizer.normalize_tree(soup)
            normalized_pages[current_url_path] = soup
            new_links = web_page_graph_handler.create_new_web_page_element(soup, base_url, current_url_path, depth)

            for new_link in new_links:
                if new_link is not None and new_link not in found_links:
                    found_links.add(new_link)
                    if utils.is_valid_relative_path(new_link):
                        url_list.append((new_link, depth + 1))
                        web_page_loader.add_url(new_link)

        index += 1
        progress_indicator.progress = index / max_searched_pages

    web_page_loader.end_tasks()
    web_page_graph_handler.resolve_all_links()
    graph_cache[identifier] = (web_page_graph_handler, normalized_pages)
    progress_indicator.finished = True


def extract_main_data(web_page_graph_handler: WebPageGraphHandler):
    web_page_data = web_page_graph_handler.get_all_web_page_data()
    web_page_data_resolved = web_page_data_processor.resolve_web_page_node_dict(web_page_graph_handler.web_page_graph,
                                                                                web_page_data)
    paragraph_elements = web_page_data_processor.map_elements(web_page_data_resolved,
                                                              web_page_data_processor.filter_for_paragraph_elements)
    data_paragraph = web_page_data_processor.map_elements(paragraph_elements,
                                                          web_page_data_processor.process_paragraph_elements)
    link_elements = web_page_data_processor.map_elements(web_page_data_resolved,
                                                         web_page_data_processor.filter_for_link_elements)
    data_link = web_page_data_processor.map_elements(link_elements,
                                                     web_page_data_processor.process_link_elements)
    return data_paragraph, data_link


def search_keyword_list(web_page_graph_handler: WebPageGraphHandler, keyword_list: [str]) -> dict:
    output = {}
    for keyword in keyword_list:
        output[keyword] = search_keyword(web_page_graph_handler, keyword)
    return output


def search_keyword(web_page_graph_handler: WebPageGraphHandler, keyword: str):
    keyword_nodes_dict = web_page_graph_handler.search_by_keyword(keyword)
    web_page_data_resolved = web_page_data_processor.resolve_web_page_node_dict(web_page_graph_handler.web_page_graph,
                                                                                keyword_nodes_dict)
    paragraph_elements = web_page_data_processor.map_elements(web_page_data_resolved,
                                                              web_page_data_processor.filter_for_paragraph_elements)
    data_paragraph = web_page_data_processor.map_elements(paragraph_elements,
                                                          web_page_data_processor.process_paragraph_elements)
    link_elements = web_page_data_processor.map_elements(web_page_data_resolved,
                                                         web_page_data_processor.filter_for_link_elements)
    data_link = web_page_data_processor.map_elements(link_elements,
                                                     web_page_data_processor.process_link_elements)
    return data_paragraph, data_link
