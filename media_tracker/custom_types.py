from enum import Enum

class OrderByType(str, Enum):
    """
    Type to establish the ordering in the database.

    It can be ASC or DESC.
    """
    ASC = 'asc'
    DESC = 'desc'