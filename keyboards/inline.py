from typing import Dict, List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_groups_kb(groups: List[Dict[str, str]]):
    """
    Function that returns a InlineKeyboardMarkup with all the groups

    Args:
        groups: list of dictionaries with ``key``: `group_name` and ``id``: `group_id`

    Returns:
        InlineKeyboardMarkup

    """
    return InlineKeyboardMarkup().add(
        *list(
            map(
                lambda group: InlineKeyboardButton(
                    group["name"], callback_data=group["id"]
                ),
                groups,
            )
        )
    )
