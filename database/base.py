import json
from os.path import exists
from pathlib import Path


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


def get_events() -> list[dict]:
    if not Path("database/events.json").is_file():
        return []
    with open("database/events.json") as f:
        return json.load(f)


def add_event(event):
    if Path("database/events.json").is_file():
        with open("database/events.json") as f:

            data = json.load(f)
    else:
        data = []
    data.append(event)
    with open("database/events.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def remove_event(event):
    if Path("database/events.json").is_file():
        with open("database/events.json") as f:
            data: list = json.load(f)
        data = list(filter(lambda x: x["id"] != event["id"], data))
        with open("database/events.json", "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
