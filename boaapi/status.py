from enum import Enum

class CompilerStatus(Enum):
    WAITING  = 1
    RUNNING  = 2
    FINISHED = 3
    ERROR    = 4

class ExecutionStatus(Enum):
    WAITING  = 1
    RUNNING  = 2
    FINISHED = 3
    ERROR    = 4

