from bs4 import BeautifulSoup, Comment

import utils


def normalize_tree(soup: BeautifulSoup):
    _clear_comments(soup)
    _remove_unwanted_tags(soup)
    _normalize_text(soup)
    _wrap_all_strings(soup)
    _remove_empty_leafs(soup)
    _clear_nesting(soup)
    _transform_structures(soup)
    _replace_leftovers(soup)  # Überlegen ob wirklich notwendig


def _clear_comments(soup: BeautifulSoup):
    body = soup.body
    comments = body.find_all(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()


def _remove_unwanted_tags(soup: BeautifulSoup):
    body = soup.body
    unwanted_elements = body.find_all(utils.state["unwanted_tags"])
    for unwanted_element in unwanted_elements:
        utils.remove_branch(unwanted_element)


def _normalize_text(soup: BeautifulSoup):
    body = soup.body
    decorator_elements = body.find_all(utils.state["normalize_text_tags"])
    for decorator_element in decorator_elements:
        decorator_element.unwrap()


def _wrap_all_strings(soup: BeautifulSoup):
    body = soup.body
    unwrapped_string_parents = body.find_all(utils.has_unwrapped_content)
    for parent in unwrapped_string_parents:
        contents = parent.contents[:]
        parent.clear()
        for content in contents:
            if isinstance(content, str) and content.strip():
                p_tag = soup.new_tag("p")
                p_tag.string = content.strip()
                parent.append(p_tag)
            else:
                parent.append(content)


def _remove_empty_leafs(soup: BeautifulSoup):
    body = soup.body
    empty_leafs = body.find_all(lambda tag: len(tag.find_all(recursive=False)) == 0 and len(utils.get_unwrapped_strings(tag)) == 0)
    for empty_leaf in empty_leafs:
        utils.remove_branch(empty_leaf)


def _clear_nesting(soup: BeautifulSoup):
    body = soup.body
    nested_elements = body.find_all(
        lambda elem: len(elem.parent.find_all(recursive=False)) == 1 and len(elem.find_all(recursive=False)) > 0)
    for nested_element in nested_elements:
        nested_element.unwrap()


def _transform_structures(soup: BeautifulSoup):
    body = soup.body
    structure_elements = utils.find_all_structures(body)
    for structure_element in structure_elements:
        leaf_elements = structure_element.find_all(lambda tag: len(utils.get_unwrapped_strings(tag)) > 0)
        new_div = soup.new_tag("div")
        for leaf_element in leaf_elements:
            new_div.append(leaf_element)
        structure_element.replace_with(new_div)


def _replace_leftovers(soup: BeautifulSoup):
    body = soup.body
    elements = body.find_all(lambda tag: tag.name == 'li' and tag.parent.name != 'ul')
    for element in elements:
        element.wrap(soup.new_tag("div"))
        element.unwrap()
