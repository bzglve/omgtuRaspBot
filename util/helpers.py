from datetime import timedelta

from database.base import add_new_kind_of_work, load_kind_of_work


def get_week_dates(base_date, start_day, end_day=None):
    monday = base_date - timedelta(days=base_date.isoweekday() - 1)
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    return week_dates[start_day - 1 : end_day or start_day]


def lesson_text(lesson):
    text_format = """🕑 *{begin_lesson} - {end_lesson}*
{kind_of_work_short} | {discipline}
👤 {lecturer_rank} {lecturer_title}
🚪 {auditorium} | {group_var}
"""

    text_vars = {
        "begin_lesson": lesson.get("beginLesson"),
        "end_lesson": lesson.get("endLesson"),
        "kind_of_work": lesson.get("kindOfWork"),
        "discipline": lesson.get("discipline"),
        "lecturer_rank": lesson.get("lecturer_rank"),
        "lecturer_title": lesson.get("lecturer_title"),
        "auditorium": lesson.get("auditorium"),
        "group": lesson.get("group"),
        "sub_group": lesson.get("subGroup"),
        "stream": lesson.get("stream"),
        "kind_of_work_oid": lesson.get("kindOfWorkOid"),
    }
    text_vars["group_var"] = text_vars.get("group") or text_vars.get("sub_group") or text_vars.get("stream")

    kind_of_work_short_vars = load_kind_of_work()
    if str(text_vars["kind_of_work_oid"]) not in kind_of_work_short_vars:
        add_new_kind_of_work(text_vars["kind_of_work_oid"], text_vars["kind_of_work"])
        kind_of_work_short_vars = load_kind_of_work()

    text_vars["kind_of_work_short"] = kind_of_work_short_vars.get(str(text_vars["kind_of_work_oid"]))

    return text_format.format(**text_vars)


def day_text(lessons):
    return "\n".join(map(lesson_text, lessons))
