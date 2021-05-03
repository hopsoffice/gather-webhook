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
config_google = config.get('google', {})
SCOPES = config_google.get('scopes')
google_config = {
    'web': {
        'client_id': os.environ.get(
            'google_client_id', config_google.get('client_id')
        ),
        'client_secret':os.environ.get(
            'google_client_secret', config_google.get('client_secret')
        ),
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://accounts.google.com/o/oauth2/token',
        'project_id': os.environ.get(
            'google_project_id', config_google.get('project_id')
        ),
    }
}
bucket_name = config.get('token_bucket_name', 'zappa-gather-webhook-token')
token_jsonname = 'token_json'


def creds_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }


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


def write(bucket, payload):
    with io.BytesIO() as stream:
        stream.write(json.dumps(payload).encode())
        stream.seek(0)
        bucket.upload_fileobj(stream, token_jsonname)


def read(bucket):
    with io.BytesIO() as stream:
        try:
            bucket.download_fileobj(token_jsonname, stream)
            stream.seek(0)
            return json.loads(stream.read())
        except:
            return None


@app.route('/auth/')
def auth_token():
    s3 = resource('s3')
    bucket = s3.Bucket(bucket_name)
    payload = {}
    creds_json = read(bucket)
    creds = None
    redirect_uri = url_for('.oauth', _external=True)
    if creds_json:
        creds = Credentials(
            token=creds_json['token'],
            refresh_token=creds_json['refresh_token'],
            token_uri=creds_json['token_uri'],
            client_id=creds_json['client_id'],
            client_secret=creds_json['client_secret'],
            scopes=creds_json['scopes']
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            write(bucket, creds_to_dict(creds))
            return 'cred refresh'
        else:
            flow = Flow.from_client_config(google_config, SCOPES)
            flow.redirect_uri = redirect_uri
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            session['state'] = state
            return redirect(authorization_url)
    return 'already valid'


@app.route('/oauth/')
def oauth():
    state = session['state']
    redirect_uri = url_for('.oauth', _external=True)
    flow = Flow.from_client_config(google_config, SCOPES, state=state)
    flow.redirect_uri = redirect_uri
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    s3 = resource('s3')
    bucket = s3.Bucket(bucket_name)
    write(bucket, creds_to_dict(credentials))
    return '200'


@app.route('/force-refresh/')
def force_refresh():
    s3 = resource('s3')
    try:
        bucket = s3.Bucket(bucket_name)
        bucket.delete_objects(
            Delete={
                'Objects': [{'Key': token_jsonname}],
                'Quiet': True,
            },
        )
    finally:
        return redirect(url_for('.auth_token'))


def get_start_dt():
    if request.form.get('start_modified') == 'y':
        start_year = request.form.get('start_year', type=int)
        start_month = request.form.get('start_month', type=int)
        start_day = request.form.get('start_day', type=int)
        start_hour = request.form.get('start_hour', type=int)
        start_min = request.form.get('start_min', type=int) or 0
        dt = datetime.datetime(
            start_year,
            start_month,
            start_day,
            start_hour,
            start_min,
            tzinfo=kst
        )
    else:
        dt = datetime.datetime.now(kst)
    return dt


@app.route('/calendar/', methods=['GET'])
def calendar():
    return render_template('calendar.html', team_mates=config['teamMates'])


@app.route('/calendar-sync/', methods=['POST'])
def calendar_sync():
    s3 = resource('s3')
    bucket = s3.Bucket(bucket_name)
    creds_json = read(bucket)
    creds = None
    if creds_json:
        creds = Credentials(
            token=creds_json['token'],
            refresh_token=creds_json['refresh_token'],
            token_uri=creds_json['token_uri'],
            client_id=creds_json['client_id'],
            client_secret=creds_json['client_secret'],
            scopes=creds_json['scopes']
        )
    if not creds:
        raise ValueError('creds failed')
    elif creds.expired and creds.refresh_token:
        creds.refresh(Request())
        write(bucket, creds_to_dict(creds))
    name = request.form.get('name')
    service = build('calendar', 'v3', credentials=creds)
    start_dt = get_start_dt()
    hour = request.form.get('hour', type=int) * 60 * 60
    minutes = request.form.get('min', type=int) * 60
    summary =  request.form.get('name')
    calendar_id = config_google.get('work_calendar_id')
    response = service.events().insert(
        calendarId=calendar_id,
        body={
            'creator': {
                'self': True,
            },
            'summary': summary,
            'start': {
                'timezone': 'Asia/Seoul',
                'dateTime': start_dt.isoformat(),
            },
            'end': {
                'timezone': 'Asia/Seoul',
                'dateTime':  (
                    start_dt + datetime.timedelta(seconds=hour + minutes)
                ).isoformat(),
            },
        },
    ).execute()
    text = config['message']['start']
    send_text(f'{name}: {text}')
    return 'done'


if __name__ == '__main__':
    app.run(debug=True)
