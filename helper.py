import json
import operator
from difflib import SequenceMatcher
import re

from requests import get


def get_common_group(groups: list):
    substring_counts = {}

    for i in range(0, len(groups)):
        for j in range(i + 1, len(groups)):
            string1 = groups[i]
            string2 = groups[j]
            match = SequenceMatcher(None, string1, string2).find_longest_match(0, len(string1), 0, len(string2))
            matching_substring = string1[match.a:match.a + match.size]
            if matching_substring not in substring_counts:
                substring_counts[matching_substring] = 1
            else:
                substring_counts[matching_substring] += 1
    max_occurring_substring = max(substring_counts.items(), key=operator.itemgetter(1))[0]
    return max_occurring_substring


page_url = 'https://rasp.omgtu.ru/api/schedule/group/'

groups_keys = [
    'stream',
    'group',
    'subGroup'
]

with open('variables.json', 'r') as f:
    groups = dict(json.load(f))

for group_id in range(max(groups.values()), max(groups.values()) + 1000):
    page_raw = get(page_url + str(group_id))
    if page_raw.status_code == 200:
        page = json.loads(page_raw.content.decode('utf-8'))
        group_candidates = []
        for p in page:
            for key in groups_keys:
                if p[key] is not None:
                    if p[key] not in group_candidates and p[key] != '':
                        group_candidates.append(p[key])
        if len(group_candidates) > 0:
            group = get_common_group(group_candidates) if len(group_candidates) > 1 else group_candidates[0]
            print(f'{group} : {group_id}')
            groups[group] = group_id
print(groups)
with open('variables.json', 'w', encoding='utf-8') as f:
    json.dump(groups, f)
