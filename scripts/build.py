import sys
import json


template = {
    'dev': {
        'app_function': 'web.app',
        'profile_name': 'hopsdev',
        'project_name': 'landing-webhook',
        'cors': True,
        'runtime': 'python3.8',
        's3_bucket': 'zappa-landing-webhook',
        'environment_variables': {
            'slack_hook': '',
            'google_client_id': '',
            'google_client_secret': '',
            'google_project_id': '',
            'deploy_url': '',
            'spreadsheet_id': ''
        }
    }
}
payload = json.loads(sys.stdin.read())

m = [
    'slack_hook',
    'google_client_id',
    'google_client_secret',
    'google_project_id',
    'deploy_url',
    'spreadsheet_id',
]


for k in m:
    template['dev']['environment_variables'][k] = payload[f'landing-webhook-{k}']


print(json.dumps(template, indent=2))
