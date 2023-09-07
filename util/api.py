import itertools
from datetime import date
from typing import Any, Dict, List, Literal, Optional

import requests


group_keys = Literal["id", "label", "description", "type"]
Group = Dict[group_keys, str]
def get_groups(query: Optional[str] = None) -> List[Group]:
    """Fetches a groups from the OmGTU API.

    Args:
        query (str, optional): string with group name

    Returns:
        list(dict): A list of dictionaries containing the group data.

    The keys of each dictionary are as follows:
        - id (str): id of the group
        - label (str): name of the group
        - description (str): description of the group
        - type (str): type of the group

    Raises:
        requests.exceptions.RequestException: if a request exception occurred
        ValueError: if the status code of the response is not 200 or no groups are available
    """  # noqa: E501

    params = {"type": "group", "term": query}

    try:
        response = requests.get("https://rasp.omgtu.ru/api/search", params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e

    if groups := list(response.json()):
        return groups
    else:
        raise ValueError("No groups available")


lesson_keys = Literal[
    "auditorium",
    "auditoriumAmount",
    "auditoriumOid",
    "author",
    "beginLesson",
    "building",
    "buildingGid",
    "buildingOid",
    "contentOfLoadOid",
    "contentOfLoadUID",
    "contentTableOfLessonsName",
    "contentTableOfLessonsOid",
    "createddate",
    "date",
    "dateOfNest",
    "dayOfWeek",
    "dayOfWeekString",
    "detailInfo",
    "discipline",
    "disciplineOid",
    "disciplineinplan",
    "disciplinetypeload",
    "duration",
    "endLesson",
    "group",
    "groupOid",
    "groupUID",
    "group_facultyoid",
    "hideincapacity",
    "isBan",
    "kindOfWork",
    "kindOfWorkComplexity",
    "kindOfWorkOid",
    "kindOfWorkUid",
    "lecturer",
    "lecturerCustomUID",
    "lecturerEmail",
    "lecturerOid",
    "lecturerUID",
    "lecturer_rank",
    "lecturer_title",
    "lessonNumberEnd",
    "lessonNumberStart",
    "lessonOid",
    "listOfLecturers",
    "modifieddate",
    "note",
    "note_description",
    "parentschedule",
    "replaces",
    "stream",
    "streamOid",
    "stream_facultyoid",
    "subGroup",
    "subGroupOid",
    "subgroup_facultyoid",
    "tableofLessonsName",
    "tableofLessonsOid",
    "url1",
    "url1_description",
    "url2",
    "url2_description",
]
Lesson = Dict[lesson_keys, Any]


def get_week_schedule(group_id: int, start: date, finish: date) -> List[List[Lesson]]:
    """Fetches the schedule for a group from the OmGTU schedule API.

    Note:
        Every list in returned list is a day containing the schedule as a dictionary

    Args:
        group_id (int): The ID of the group whose schedule is to be fetched.
        start (date): The start date of the schedule.
        finish (date): The end date of the schedule.

    Returns:
        List[List[Lesson]]: A list of lists of dictionaries containing the schedule data

    Raises:
        requests.exceptions.RequestException: If there is an error in the HTTP request.
        ValueError: If the response from the API is empty.

    """

    params = {
        "lng": 1,
        "start": start.strftime("%Y.%m.%d"),
        "finish": finish.strftime("%Y.%m.%d"),
    }

    try:
        response = requests.get(f"https://rasp.omgtu.ru/api/schedule/group/{group_id}", params=params)
    except requests.exceptions.RequestException as e:
        raise e

    if schedule := response.json():
        return [list(day_schedule) for _, day_schedule in itertools.groupby(schedule, key=lambda k: k["date"])]
    else:
        raise ValueError("No schedule available")


def get_day_schedule(group_id: int, schedule_date: date) -> List[Lesson]:
    """Fetches the schedule for a group from the OmGTU schedule API.

    Args:
        group_id (int): The ID of the group whose schedule is to be fetched.
        schedule_date (date): The date of the schedule.

    Returns:
        List[Lesson]: A list of dictionaries containing the schedule data.

    Raises:
        requests.exceptions.RequestException: If there is an error in the HTTP request.
        ValueError: If the response from the API is empty.

    """

    return get_week_schedule(group_id, schedule_date, schedule_date)[0]
