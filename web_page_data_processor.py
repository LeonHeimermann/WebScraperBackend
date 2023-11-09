from typing import Callable

from networkx import DiGraph
from web_page_graph_handler import LinkElement, ParagraphElement, DataElement


def resolve_web_page_node_dict(web_page_graph: DiGraph, web_page_node_dict: dict) -> dict:
    output = {}
    for web_page_node_id, container_node_dict in web_page_node_dict.items():
        url = web_page_graph.nodes[web_page_node_id]['data'].url
        output[url] = resolve_container_node_dict(web_page_graph, container_node_dict)
    return output


def resolve_container_node_dict(web_page_graph: DiGraph, container_node_dict: dict) -> [[DataElement]]:
    return [resolve_data_node_list(web_page_graph, data_node_list) for data_node_list in container_node_dict.values()]


def resolve_data_node_list(web_page_graph: DiGraph, data_node_list: [int]) -> [DataElement]:
    return [web_page_graph.nodes[data_node_id]['data'] for data_node_id in data_node_list]


def map_elements(web_page_resolved: dict, map_func: Callable) -> dict:
    output = {}
    for web_page_key, web_page_value in web_page_resolved.items():
        mapped_elements = []
        for data_list in web_page_value:
            mapped_element = map_func(data_list)
            if mapped_element:
                mapped_elements.append(map_func(data_list))
        if mapped_elements:
            output[web_page_key] = mapped_elements
    return output


def filter_for_paragraph_elements(data_list: [DataElement]) -> [ParagraphElement]:
    return list(filter(lambda data_element: isinstance(data_element, ParagraphElement), data_list))


def process_paragraph_elements(paragraph_element_list: [ParagraphElement]) -> [ParagraphElement]:
    return list(map(lambda link_element: link_element.data, paragraph_element_list))


def filter_for_link_elements(data_list: [DataElement]) -> [LinkElement]:
    return list(filter(lambda data_element: isinstance(data_element, LinkElement), data_list))


def process_link_elements(link_element_list: [LinkElement]) -> [LinkElement]:
    output = []
    for link_element in link_element_list:
        if link_element.href:
            output.append((link_element.data, link_element.href))
    return output
