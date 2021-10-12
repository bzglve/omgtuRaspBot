import json

variables = {
    'groups': {},
    'persons': {},
    'rooms': {},
    'admins': {
        '389026886': 'bzglve',
        '700440368': 'rumbleofgunlock'
    },
    'ban_list': {}
}

with open('variables.json', 'r') as f:
    variables['groups'] = json.load(f)['groups']
for key, val in variables.items():
    print(key, val)

with open('variables.json', 'w') as f:
    json.dump(variables, f)
