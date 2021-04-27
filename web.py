import datetime
import functools
import io
import json
import os
import urllib.parse
import urllib.request

from boto3 import resource
from flask import Flask, redirect, render_template, request, session, url_for
from flask_cors import CORS
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)
app.secret_key = 'owefowijefweofijwefoij'
slack_hook = os.environ.get('slack_hook')
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


return_ = functools.partial(meta, text=':백:')
return_.__name__ = 'return'
start = functools.partial(meta, text='근무 시작합니다.')
start.__name__ = 'start'

app.route('/start/<name>/', methods=['GET'])(start)
app.route('/return/<name>/', methods=['GET'])(return_)


@app.route('/eat-html/', methods=['GET'])
def eat_html():
    return render_template('eat.html')


@app.route('/rest-html/', methods=['GET'])
def rest_html():
    return render_template('rest.html')


@app.route('/do-html/', methods=['GET'])
def do_html():
    return render_template('do.html')


@app.route('/some/', methods=['POST'])
def some():
    name = request.form.get('name')
    time = request.form.get('time')
    action = request.form.get('act')
    dt = datetime.datetime.now(kst) + \
            datetime.timedelta(seconds=int(time) * 60)
    send_text(
        '*{0}*: {2} {1:%H}시 {1:%M}분에 돌아올게요.'.format(
            name, dt, action
        )
    )
    return 'done'


if __name__ == '__main__':
    app.run(debug=True)
