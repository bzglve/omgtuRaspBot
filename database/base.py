import json
from os.path import exists


def change_group(user_id: int, group_id: int):
    data = {}
    if exists("data/data.json"):
        with open("data/data.json", "r") as f:
            data = json.load(f)
    data[str(user_id)] = group_id
    with open("data/data.json", "w") as f:
        json.dump(data, f, indent=4)


def get_user_group(user_id: int):
    if exists("data/data.json"):
        with open("data/data.json", "r") as f:
            data = json.load(f)
        return data.get(str(user_id))


def load_kind_of_work() -> dict:
    with open("data/kind_of_work.json") as f:
        return json.load(f)


def add_new_kind_of_work(id, kind_of_work):
    with open("data/kind_of_work.json") as f:
        data = json.load(f)
    data[id] = kind_of_work
    with open("data/kind_of_work.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
