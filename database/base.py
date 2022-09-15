import json
from os.path import exists


def change_group(user_id: int, group_id: int):
    data = {}
    if exists("database/data.json"):
        with open("database/data.json", "r") as f:
            data = json.load(f)
    data[str(user_id)] = group_id
    with open("database/data.json", "w") as f:
        json.dump(data, f, indent=4)


def get_user_group(user_id: int):
    if exists("database/data.json"):
        with open("database/data.json", "r") as f:
            data = json.load(f)
        return data.get(str(user_id))
