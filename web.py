import base64
import datetime
import functools
import io
import json
import os
import pathlib
import urllib.parse
import urllib.request

from boto3 import resource
from flask import Flask, redirect, render_template, request, session, url_for
from flask_cors import CORS
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

try:
    with pathlib.Path('./resource.json').open('r') as f:
        config = json.loads(f.read())
except:
    raise RuntimeError('resource.json이 필요합니다')

app = Flask(__name__)
CORS(app)
app.secret_key = base64.b64encode(os.urandom(64)).decode()
slack_hook = os.environ.get('slack_hook', config.get('slack_hook'))
kst = datetime.timezone(datetime.timedelta(hours=9))


@app.route('/')
def main():
    return 'pong'


def send_text(text: str):
    req = urllib.request.Request(
        slack_hook,
        data=json.dumps({'text': text}).encode('utf-8'),
        method='POST',
        headers={'Content-Type': 'application/json'}
    )
    try:
        response = urllib.request.urlopen(req)
    except:
        pass
    return response


def meta(text: str, name: str):
    send_text(f'{name}: {text}')
    return '200'


return_ = functools.partial(meta, text=config['message']['return'])
return_.__name__ = 'return'
start = functools.partial(meta, text=config['message']['start'])
start.__name__ = 'start'
end = functools.partial(meta, text=config['message']['end'])
end.__name__ = 'end'

app.route('/start/<name>/', methods=['GET'])(start)
app.route('/return/<name>/', methods=['GET'])(return_)
app.route('/end/<name>/', methods=['GET'])(end)


@app.route('/eat/', methods=['GET'])
def eat_html():
    return render_template(
        'eat.html',
        team_mates=config['teamMates'],
        prefix=config['prefix']['eat']
    )


@app.route('/rest/', methods=['GET'])
def rest_html():
    return render_template(
        'rest.html',
        team_mates=config['teamMates'],
        prefix=config['prefix']['rest']
    )


@app.route('/do/', methods=['GET'])
def do_html():
    return render_template('do.html', team_mates=config['teamMates'])


@app.route('/action/', methods=['POST'])
def make_action():
    name = request.form.get('name')
    time = request.form.get('time')
    action = request.form.get('act')
    dt = datetime.datetime.now(kst) + \
            datetime.timedelta(seconds=int(time) * 60)
    send_text(config['message']['action'].format(name, action, dt))
    return 'done'


if __name__ == '__main__':
    app.run(debug=True)
