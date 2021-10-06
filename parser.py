import json

from requests import get

page = get('https://rasp.omgtu.ru/api/schedule/group/464')
print(page.status_code)
shedule = json.loads(page.content.decode('utf-8'))
print(type(shedule))
for i in shedule:
    for key in i.keys():
        print(key, i[key])
    print('#' * 10)

# TODO Найти поддомены shedule/... для получения по преподам.группам и тп
# TODO По-человечески парсить
