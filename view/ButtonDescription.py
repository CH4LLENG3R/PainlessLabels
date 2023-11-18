class ButtonDescription:
    def __init__(self, name: str, value: str, shortcut: str, group_id: str):
        self.__name = name
        self.__value = value
        self.__shortcut = shortcut
        self.__group_id = group_id

    def get_name(self):
        return self.__name

    def get_value(self) -> str:
        return self.__value

    def get_shortcut(self):
        return self.__shortcut

    def get_group_id(self):
        return self.__group_id