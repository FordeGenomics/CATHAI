import requests
from app import csrf, app

from flask import Blueprint, Response, request
from flask_login import login_required

cathai = Blueprint('cathai', __name__)

def process_request(path, request, PROXY_URL):
    headers = {}
    headers['Cookie'] = dict(request.headers)['Cookie']
    headers['Referer'] = PROXY_URL
    query = request.query_string.decode("utf-8")
    if len(query) > 0:
        if '?' in path:
            path = path + "&" + query
        else:
            path = path + "?" + query
    if request.method =='GET':
        resp = requests.get(path, headers=headers)
    elif request.method =='POST':
        resp = requests.post(path, headers=headers, data=dict(request.form))
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in  resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response


@cathai.route('/demo/',methods=['GET','POST'])
@csrf.exempt
def demo_base():
    PROXY_URL = 'http://127.0.0.1:3840/'
    path = f'{PROXY_URL}'
    return process_request(path, request, PROXY_URL)

@cathai.route('/demo/<path:path>',methods=['GET','POST'])
@csrf.exempt
def demo_files(path):
    PROXY_URL = 'http://127.0.0.1:3840/'
    path = f'{PROXY_URL}{path}'
    return process_request(path, request, PROXY_URL)

if app.config['STAND_ALONE'] == False:
    @cathai.route('/',methods=['GET','POST'])
    @csrf.exempt
    @login_required
    def index():
        PROXY_URL = 'http://127.0.0.1:3838/'
        path = f'{PROXY_URL}'
        return process_request(path, request, PROXY_URL)

    @cathai.route('/<path:path>',methods=['GET','POST'])
    @csrf.exempt
    @login_required
    def cathai_files(path):
        PROXY_URL = 'http://127.0.0.1:3838/'
        path = f'{PROXY_URL}{path}'
        return process_request(path, request, PROXY_URL)
else:
    @cathai.route('/',methods=['GET','POST'])
    @csrf.exempt
    def index():
        PROXY_URL = 'http://127.0.0.1:3838/'
        path = f'{PROXY_URL}'
        return process_request(path, request, PROXY_URL)

    @cathai.route('/<path:path>',methods=['GET','POST'])
    @csrf.exempt
    def cathai_files(path):
        PROXY_URL = 'http://127.0.0.1:3838/'
        path = f'{PROXY_URL}{path}'
        return process_request(path, request, PROXY_URL)
