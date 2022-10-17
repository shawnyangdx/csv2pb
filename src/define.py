from enum import Enum

class TableLineType(Enum):
    DataName = 0
    DataType = 1
    CSType = 2
    Description = 3
    Max = 4

class CSType(Enum):
    cs = 0, #共用
    c = 1 #只有客户端
    s = 2, #只有服务器