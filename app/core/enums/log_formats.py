from enum import Enum


class LogFormat(Enum):
    # Application specific formats
    APP_DEFAULT = "%(levelname)s | %(asctime)s | %(name)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s"


class UvicornFormat(Enum):
    COLORED_MINIMAL = "%(levelname)s | %(message)s"
    COLORED_DETAILED = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
