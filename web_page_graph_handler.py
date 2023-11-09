import networkx as nx

import utils


class DataElement:
    def __init__(self, data):
        self.data = data


class LinkElement(DataElement):
    def __init__(self, href, data):
        super().__init__(data)
        self.href = href


class ParagraphElement(DataElement):
    def __init__(self, data):
        super().__init__(data)


class ContainerElement:
    def __init__(self, block_id):
        self.block_id = block_id


class WebPageElement:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth


class WebPageGraphHandler:
    def __init__(self):
        self.web_page_graph = nx.DiGraph()
        self.node_id_counter = utils.Counter()
        self.root_nodes = {}
        self.link_nodes = {}
        self.data_nodes = {}

    def create_new_web_page_element(self, soup, base_url, url_path, depth):
        new_links = set()

        web_page_element = WebPageElement(url_path, depth)
        web_page_element_id = self.create_new_node(data=web_page_element)
        self.root_nodes[url_path] = web_page_element_id

        body = soup.body
        leaf_first_children = body.find_all(
            lambda tag: len(utils.get_unwrapped_strings(tag)) > 0 and len(tag.find_previous_siblings()) == 0)
        for block_id, first_children in enumerate(leaf_first_children):
            container_element = ContainerElement(block_id)
            container_element_id = self.create_new_node(data=container_element)
            self.web_page_graph.add_edge(web_page_element_id, container_element_id)

            parent = first_children.parent
            leaf_elements = parent.find_all(recursive=False)
            for leaf_element in leaf_elements:
                content = utils.get_unwrapped_strings(leaf_element)
                if not content == []:
                    if leaf_element.name == 'a' and leaf_element.get('href') is not None:
                        href_normalized = utils.normalize_url(leaf_element.get('href'), base_url)
                        data_element = LinkElement(href=href_normalized, data=content[0])
                        data_element_id = self.create_new_node(data_element)
                        if href_normalized in self.link_nodes:
                            self.link_nodes[href_normalized].append(data_element_id)
                        else:
                            self.link_nodes[href_normalized] = [data_element_id]
                        new_links.add(href_normalized)
                    else:
                        data_element = ParagraphElement(data=content[0])
                        data_element_id = self.create_new_node(data_element)

                    if content[0] in self.data_nodes:
                        self.data_nodes[content[0]].add(data_element_id)
                    else:
                        self.data_nodes[content[0]] = {data_element_id}
                    self.web_page_graph.add_edge(container_element_id, data_element_id)
        return new_links

    def resolve_all_links(self):
        for link_node_url, link_node_ids in self.link_nodes.items():
            if link_node_url in self.root_nodes:
                for link_node_id in link_node_ids:
                    self.web_page_graph.add_edge(link_node_id, self.root_nodes[link_node_url])

    def get_node_data(self, node_id):
        return self.web_page_graph.nodes[node_id]['data']

    def create_new_node(self, data):
        node_id = self.node_id_counter.value
        self.web_page_graph.add_node(node_id, data=data)
        self.node_id_counter.increment()
        return node_id

    def search_by_keyword(self, key_word):
        keyword_nodes = self.get_nodes_by_keyword(key_word)
        container_nodes = set()
        for keyword_node in keyword_nodes:
            container_nodes.add(self.get_container_node_by_data_node(keyword_node))
            lower_web_page_nodes = list(self.web_page_graph.successors(keyword_node))
            if lower_web_page_nodes:
                lower_web_page_node = lower_web_page_nodes[0]
                container_nodes.update(self.get_web_page_data(lower_web_page_node))
        all_container_data = self.get_all_container_data(container_nodes)
        web_page_nodes = {}
        for container_id, data_ids in all_container_data.items():
            web_page_node_id = self.get_web_page_node_by_container_node(container_id)
            if web_page_node_id not in web_page_nodes:
                web_page_nodes[web_page_node_id] = {}
            web_page_nodes[web_page_node_id][container_id] = data_ids
        return web_page_nodes

    def get_container_node_by_data_node(self, data_node_id):
        return list(self.web_page_graph.predecessors(data_node_id))[0]

    def get_web_page_node_by_container_node(self, container_node_id):
        return list(self.web_page_graph.predecessors(container_node_id))[0]

    def get_nodes_by_keyword(self, key_word):
        output = set()
        for key in self.data_nodes.keys():
            if key_word.lower() in key.lower():
                output.update(self.data_nodes[key])
        return output

    def get_all_web_page_data(self):
        output = {}
        for web_page_node in self.root_nodes.values():
            output[web_page_node] = self.get_web_page_data(web_page_node)
        return output

    def get_web_page_data(self, web_page_node):
        container_nodes = list(self.web_page_graph.successors(web_page_node))
        return self.get_all_container_data(container_nodes)

    def get_all_container_data(self, container_nodes):
        output = {}
        for container_node in container_nodes:
            container_data = self.get_container_data(container_node)
            if container_data:
                output[container_node] = container_data
        return output

    def get_container_data(self, container_node):
        output = []
        child_nodes = self.web_page_graph.successors(container_node)
        for child_node in child_nodes:
            output.append(child_node)
        return output
