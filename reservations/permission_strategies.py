from abc import ABCMeta, abstractmethod


class SpacePermissionChecker(metaclass=ABCMeta):
    """
    공간에 대한 예약 권한을 확인하기 위한 Strategy interface
    """

    @abstractmethod
    def check(self, space, user) -> bool:
        """
        해당 space에 대한 user의 권한이 유효함을 확인하는 추상 메서드
        :param space: 권한을 확인할 대상 space
        :param user: 권한을 확인할 대상 user(member)
        :return: 유효한 경우 True, 그렇지 않을 경우 False를 반환
        """
        pass


class IncludeSinglePermissionChecker(SpacePermissionChecker):
    def check(self, space, user) -> bool:
        """
        해당 space가 요구하는 단 하나의 권한을 사용자가 포함하고 있는지 확인하는 메서드
        """
        # case 1. 아예 요구되는 권한이 없는 경우
        if space.required_permission is None:
            return True
        # case 2. 요구되는 권한을 사용자가 가지고 있는 경우
        elif space.required_permission in user.get_permission_tags_in_group(space.group):
            return True
        # 조건을 만족하지 못할 경우 False를 반환
        else:
            return False
