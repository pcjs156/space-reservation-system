from typing import List

from users.models import Group, SystemUser


def sort_group_member(group: Group, members: List[SystemUser], topmost_manager: bool):
    manager = group.manager
    if topmost_manager:
        members.sort(key=lambda m: (manager != m, m.id))
    else:
        members.sort(key=lambda m: m.id)
