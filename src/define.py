from enum import Enum

MaxTableInfoLineNum = 3

class TableLineType(Enum):
    DataName = 0
    DataType = 1
    CSType = 2
    Max = 3

class DataType(Enum):
    Single = 0 #单一变量，如int， float， string等
    List = 1