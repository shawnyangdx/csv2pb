class DataColumn(object):
    def __init__(self, index, name, ignore):
        self.startIndex = index
        self.datalength = 1
        self.name = name
        self.ignore = ignore
    
    def __str__(self):
        return 'Name:%s, StartIndex:%d, DataLength:%d' %(self.name, self.startIndex, self.datalength)

    ###newindex为list下标
    def updatelist(self, tableindex, newindex):
        if tableindex - self.startIndex != self.datalength != newindex:
            print("表格list数据下标非连续，请检查类型配置.")
            return False
     
        self.datalength = tableindex - self.startIndex + 1
        return True


