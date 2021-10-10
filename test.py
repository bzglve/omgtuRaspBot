import json

with open('variables.json', 'r') as f:
    groups = json.load(f)

groups = {k: v for k, v in sorted(groups.items(), key=lambda item: item[1])}

for group, group_id in groups.items():
    try:
        if len(group.split('-')[1]) == 3 and 'Поток' not in group:
            print(group_id, group)
    except IndexError:
        pass

print('#'*64)

for group, group_id in groups.items():
    error = False
    try:
        if len(group.split('-')[1]) != 3 or 'Поток' in group:
            error = True
    except IndexError:
        error = True
    if error:
        print(group_id, group)

# {k: v for k, v in sorted(x.items(), key=lambda item: item[1])}
