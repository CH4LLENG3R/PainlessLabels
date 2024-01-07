from controller.Enumerators import Action, Status


class UserMediator:
    def __init__(self, action: Action = None, status: Status = None, filename: str = '', reason: str = '', annotation: str = '', position: int = 0):
        self.__action = action
        self.__status = status
        self.__filename = filename
        self.__reason = reason
        self.__annotation = annotation
        self.__progress = ''
        self.__position = position

    def set_action(self, action: Action):
        self.__action = action

    def get_action(self) -> Action:
        return self.__action

    def set_status(self, status: Status):
        self.__status = status

    def get_status(self) -> Status:
        return self.__status

    def set_filename(self, filename: str):
        self.__filename = filename

    def get_filename(self) -> str:
        return self.__filename

    def set_reason(self, reason: str):
        self.__reason = reason

    def get_reason(self) -> str:
        return self.__reason

    def set_annotation(self, annotation: str):
        self.__annotation = annotation

    def get_annotation(self) -> str:
        return self.__annotation

    def is_complete(self) -> bool:
        return self.__reason != ''

    def set_progress(self, progress: str):
        self.__progress = progress

    def get_progress(self) -> str:
        return self.__progress

    def set_position(self, position: int):
        self.__position = position

    def get_position(self) -> int:
        return self.__position

    def __str__(self):
        return 'action: {}, reason: {}, annotaion: {}'.format(self.__action.name, self.__reason, self.__annotation)
