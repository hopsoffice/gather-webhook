import pathlib
import sys
import json


template = {
    'dev': {
        'app_function': 'web.app',
        'profile_name': 'gather_webhook',
        'project_name': 'gather-webhook',
        'cors': True,
        'runtime': 'python3.8',
        's3_bucket': 'zappa-gather-webhook',
        'environment_variables': {
            'slack_hook': ''
        }
    }
}

with pathlib.Path('./resource.json').open('r') as f:
    config = json.loads(f.read())


settings = template.copy()
settings['dev']['environment_variables']['slack_hook'] = config['slack_hook']

print(json.dumps(settings, indent=2))
