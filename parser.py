import json

from requests import get

# page_raw = get('https://rasp.omgtu.ru/api/schedule/group/464')
page_raw = get('https://rasp.omgtu.ru/api/schedule/group/39')
print(page_raw.status_code)
page = json.loads(page_raw.content.decode('utf-8'))

keys = [
    'auditorium',
    'beginLesson',
    'date',
    'dayOfWeekString',
    'discipline',
    'endLesson',
    'kindOfWork',
    'lecturer',
    'stream',
    'group',
    'subGroup'
]

groups_candidates = []

for p in page:
    # print(p)
    if p['dayOfWeekString'] in ['Чт', 'Пт'] or True:
        for key in keys:
            if p[key] is not None:
                print(p[key])
                if key in ['stream', 'group', 'subGroup']:
                    if p[key] not in groups_candidates:
                        groups_candidates.append(p[key])
        print('#' * 10)

print(groups_candidates)

# TODO Найти поддомены shedule/... для получения по преподам.группам и тп
# TODO По-человечески парсить
