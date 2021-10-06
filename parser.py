from requests import get
import json
page = get('https://rasp.omgtu.ru/api/schedule/group/464')
print(page.status_code)
shedule = json.loads(page.content.decode('utf-8'))
print(type(shedule))
for i in shedule:
    for key in i.keys():
        print(key, i[key])
    print('#'*10)
