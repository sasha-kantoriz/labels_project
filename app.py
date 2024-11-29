import os
import json
import pathlib
import requests
from uuid import uuid4
from time import sleep
from flask import Flask, render_template, request, jsonify


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        record_id = request.form.get('id-input')
        request_id = uuid4().hex
        response = requests.get(f'https://hook.eu1.make.com/{os.getenv("make_token")}', params={'request_id': request_id, 'idmagazzino': record_id})
        for _ in range(20):
            if os.path.exists(f'/home/printer/data/{request_id}.json'):
                with open(f'/home/printer/data/{request_id}.json', 'r') as f:
                    data = json.loads(f.read())
                    return jsonify(data)
            sleep(1)
        return jsonify({'error': 'Request timed out'})
    return render_template('index.html')

@app.route('/callback', methods=['POST'])
def callback():
    pathlib.Path('/home/printer/data').mkdir(exist_ok=True)
    data = request.form
    with open(f'/home/printer/data/{data["request_id"]}.json', 'w') as f:
        f.write(json.dumps(data))
    return data
