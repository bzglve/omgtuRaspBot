from datetime import timedelta


def get_week_dates(base_date, start_day, end_day=None):
    monday = base_date - timedelta(days=base_date.isoweekday() - 1)
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    return week_dates[start_day - 1 : end_day or start_day]


def lesson_text(lesson):
    # "subGroup"
    text = ""
    text += f'*{lesson.get("beginLesson")}* *-* *{lesson.get("endLesson")}*'
    text += f'        _{lesson.get("auditorium")}_'
    if lesson.get("subGroup"):
        text += f'        *({lesson.get("subGroup")})*'
    if lesson.get("stream"):
        text += f'        *({lesson.get("stream")})*'
    text += "\n"
    text += f'{lesson.get("discipline")}\n'
    if lesson.get("lecturer_title"):
        text += f'{lesson.get("lecturer_rank")} {lesson.get("lecturer_title")}\n'

    return text


def day_text(lessons):
    return "\n".join(map(lesson_text, lessons))
