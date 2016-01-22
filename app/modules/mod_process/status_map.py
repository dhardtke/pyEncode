from enum import Enum


# this Enum maps the different file statuses to their integer values in the database
class StatusMap(Enum):
    queued = 0
    failed = 1
    processing = 2
    finished = 3
