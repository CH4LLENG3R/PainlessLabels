from enum import Enum


class Action(Enum):
    REMOVE = 0
    KEEP = 1
    PREVIOUS = 2
    NEXT = 3


class Status(Enum):
    NOT_REVIEWED = 0
    TO_KEEP = 1
    TO_REMOVE = 2
