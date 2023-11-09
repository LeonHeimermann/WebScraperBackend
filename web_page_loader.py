import concurrent.futures
import threading
import requests
from bs4 import BeautifulSoup
import atexit


class WebPageLoader:
    def __init__(self, identifier, base_url):
        self.base_url = base_url
        self.web_page_dict = {}
        self.event_dict = {}
        self.identifier = identifier

    def _process_url(self, url_path):
        response = requests.get(self.base_url + url_path)
        html_content = response.text
        self.web_page_dict[url_path] = BeautifulSoup(html_content, 'html.parser')
        del tasks[self.identifier][url_path]
        self.event_dict[url_path].set()

    def add_url(self, url_path):
        self.event_dict[url_path] = threading.Event()
        if self.identifier not in tasks:
            tasks[self.identifier] = {}
        task = executor.submit(self._process_url, url_path)
        tasks[self.identifier][url_path] = task

    def get_url(self, url_path):
        self.event_dict[url_path].wait()
        return self.web_page_dict[url_path]

    def end_tasks(self):
        own_tasks = tasks[self.identifier]
        for task in own_tasks.values():
            task.cancel()


def cleanup(*args):
    executor.shutdown(wait=False, cancel_futures=True)


executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
tasks = {}
atexit.register(cleanup)
