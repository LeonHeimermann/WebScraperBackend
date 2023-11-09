import json

from flask import Flask, request
from flask_cors import CORS

import app_data_handler
import utils

app = Flask(__name__)
CORS(app)


@app.route('/create-graph', methods=['POST'])
def create_graph():
    base_url, url_path, max_depth, max_searched_pages = utils.extract_identifier_data(request.get_json())
    app_data_handler.create_web_page_graph(base_url, url_path, max_depth, max_searched_pages)
    return 'Process started', 200


@app.route('/progress', methods=['GET'])
def get_progress():
    base_url, url_path, max_depth, max_searched_pages = utils.extract_identifier_data(request.args)
    progress_indicator = app_data_handler.get_progress(base_url, url_path, max_depth, max_searched_pages)
    return json.dumps(progress_indicator.to_dict(), indent=4), 200


@app.route('/data', methods=['GET'])
def get_main_data():
    base_url, url_path, max_depth, max_searched_pages = utils.extract_identifier_data(request.args)
    main_data = app_data_handler.get_main_data(base_url, url_path, max_depth, max_searched_pages)
    if main_data is None:
        return "", 400
    main_data_response = {
        "ri": main_data[0],
        "links": main_data[1]
    }
    return main_data_response, 200


@app.route('/keywords', methods=['GET'])
def search_keywords():
    base_url, url_path, max_depth, max_searched_pages = utils.extract_identifier_data(request.args)
    keyword_list_str = request.args.get('keywords')
    if not keyword_list_str:
        return "", 400
    keyword_list = list(map(lambda keyword: keyword.strip(), keyword_list_str.split(',')))
    keyword_data = app_data_handler.search_keywords(base_url, url_path, max_depth, max_searched_pages, keyword_list)
    if keyword_data is None:
        return "", 400
    return keyword_data, 200


@app.route('/normalized-page', methods=['GET'])
def get_normalized_page():
    base_url, url_path, max_depth, max_searched_pages = utils.extract_identifier_data(request.args)
    requested_page_url = request.args.get('normalized_page_url')
    normalized_page = app_data_handler.get_normalized_page(base_url, url_path, max_depth, max_searched_pages, requested_page_url)
    return normalized_page


if __name__ == '__main__':
    app.run(debug=True)
