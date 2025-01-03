#coding=utf-8

#python版本：3.10.1以上
#请安装python环境，https://www.python.org/downloads/

#protobuf版本：4.21.6
#如无pb环境，在cmd命令行中执行下列信息：
#pip install protobuf==4.21.6

#version=1.0.3
import csv 
import os, sys
import json
import re
import define as Define
import data_column as DataColumn
import template
import shutil

def  write_file_context(str):
    if targetApi != 'python':
        return

    with open('pbfile/files.py', 'a') as fileContext:
        fileContext.write('\n')
        fileContext.write(str)

def get_type_desc(type):
    if type == 'int':
        return 'int32'
    elif type == 'bool':
        return 'bool'
    elif type == 'float':
        return 'float'
    elif type == 'double':
        return 'double'
    elif type == 'string':
        return 'string'    
    else:
        print("配置中填写了一个未知的数据类型%s", type)

    return ''

def  create_data_tuple(datas, datatypes):
    tuple = ()
    for index, type in enumerate(datatypes):
        # if ignoreindex.count(index) > 0:
        #     continue

        if type == 'int':
            tuple += (int(datas[index]),)
        elif type == 'bool':
            tuple += ((True if int(datas[index]) == 1 else False),)
        elif type == 'float':
            tuple += (float(datas[index]),)
        elif type == 'double':
            tuple += (float(datas[index]),)
        elif type == 'string':
            # tuple += (bytes(datas[index], encoding='UTF-8'),)
            tuple += (datas[index],)
        else:
            print("配置中填写了一个未知的数据类型%s", type)
    
    return tuple
            

def generate_data(fileName, datas):
    dataName = datas[Define.TableLineType.DataName.value]
    dataType = datas[Define.TableLineType.DataType.value]
    dataType.pop(0)
    #生成pbscript并塞入表格数据
    key = fileNameToKey[fileName]
    if key != None:
        keyindex = 0
    tuplelist = []
    for index, data in  enumerate(datas):
        if index <= Define.TableLineType.Max.value:
            continue

        data.pop(0)
        #如果是注释
        if data[0].lstrip()[0] == "#":
            continue

        if len(dataType) > len(data):
            print("配置数据缺失，行数：%d", index)
        

        t = create_data_tuple(data, dataType)
        tuplelist.append(t)

    fileWithoutExt = fileName.replace('.csv', '')
    exec("handleContext.serialize2pb%s(keyindex, tuplelist, cfg)" % (fileWithoutExt))
    print(fileName)

def find_column_by_name(name, columns):
    for c in columns:
        if c.name == name:
            return c
    
    return None

def parse_dataname(dataName):
    allColumns = []
    for index, name in enumerate(dataName):
        findindex = name.find('_')
        if findindex >= 0:
            strlist = name.split('_')
            if len(strlist) == 2: #list格式
                newname = strlist[0]
                newindex = int(strlist[1])
                findcolumn = find_column_by_name(newname, allColumns)
                if findcolumn == None:
                    ignoreindex = name.find('#')
                    actname = newname
                    if ignoreindex >= 0:
                        actname = newname.replace("#", '')
                    findcolumn = DataColumn.DataColumn(index, actname, ignoreindex >= 0)
                    allColumns.append(findcolumn)
                else:
                    findcolumn.updatelist(index, newindex)
        else:
            ignoreindex = name.find('#')
            actname = name
            if ignoreindex >= 0:
                actname = name.replace("#", '')
            allColumns.append(DataColumn.DataColumn(index, actname, ignoreindex >= 0))

    return allColumns

def generate_proto(fileName, lines):
    if len(lines) < Define.TableLineType.Max.value:
        print("表头行数少于3行，请检查表配置（标题，类型，cs类型）")
        return False
    
    dataName = lines[Define.TableLineType.DataName.value].replace('\n', '').split(',')
    dataName.pop(0)
    dataType = lines[Define.TableLineType.DataType.value].replace('\n', '').split(',')
    dataType.pop(0)
    csType = lines[Define.TableLineType.CSType.value].replace('\n', '').split(',')
    csType.pop(0)
    descriptions = lines[Define.TableLineType.Description.value].replace('\n', '').split(',')
    if len(descriptions) <= 0:
        print("描述缺少关键字，请检查表格是否配置了key值.")
        return False

    descriptions = descriptions[1].split(';')

    key = descriptions[0].split('=')[1]
    if key != dataName[0]:
        print("表格key值不对应，请检查表格是否配置了key值对应字段名，及是否名称相同.")
        return False

    if len(dataName) != len(dataType) != len(csType):
        print("表头列数量不一致，请检查配置")
        return False

    fileNameToKey[fileName] = key
    keyType = dataType[0]
    
    allColumns = parse_dataname(dataName)

    #生成pb格式
    protoName = 'Tab_' + fileName.replace('.csv', '.proto')
    protodir = os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg['protodir'])
    if not os.path.exists(protodir):
        os.mkdir(protodir)
    protofile = os.path.join(protodir, protoName)
    with open(protofile, 'w') as file:
        #pb抬头
        str = ""
        str += ('syntax = "proto3";\n')
        str += 'package %s;' % cfg['packageName']
        str += '\n'



        #生成包含struct的数据格式
        title = '%s%s\n' % ((protoName.replace('.proto',''),'{'))
        str += 'message '
        str += title.title()
                #解析表头生成struct
        structName = 'Data'
        str += '    \n'
        str += '    message '
        str += ' {}{}\n'.format(structName,'{')
        for index, c in enumerate(allColumns):
            if c.ignore:
                continue
            t = dataType[c.startIndex]
            cst = csType[c.startIndex]
            if cst == "": #如果为空，则不加数据
                print("有数据cstype未标识，默认为客户端-服务器（cs）类型")
                cst = "cs"

            str += "        repeated " if c.datalength > 1 else "       optional "
            str += get_type_desc(t)
            str += ' '
            str +=  c.name.title()
            str += '     = {};\n'.format(index + 1)           
        str += '    }\n'
        str += '    \n'
        str += ' repeated Data datas = 1;\n'
        str += '}\n'
        file.write(str)
    
    write_file_context(template.import_pb2(fileName))
    write_file_context(template.serialize2db_message(fileName, protoName.replace('.proto','').title(), structName, allColumns))

    rootpath = os.path.dirname(os.path.abspath(__file__))
    compiler = os.path.join(rootpath, cfg['protocompiler'])

    protoName = 'Tab_' + fileName.replace('.csv', '.proto')
    protodir = os.path.join(rootpath, cfg['protodir'])
    dir = '%sdir' % (targetApi)
    tmpdir = os.path.join(rootpath, cfg[dir])
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)

    command = '%s\protoc -I=%s --%s_out=%s %s\%s' %(compiler, protodir, targetApi, tmpdir, protodir, protoName)
    os.system(command)
    print(command)

    delectFiles.append('pbfile/Tab_%s_pb2.py' %(fileName.replace('.csv', '')))
    return True
#

def clear_pbfile_dir():
    if not os.path.exists('pbfile'):
        return
    
    for fileName in os.listdir('pbfile'):
        if fileName.find('pb2') >= 0:
            os.remove(os.path.join('pbfile', fileName))

        if fileName.find('files') >=0:
            os.remove(os.path.join('pbfile', fileName))

def clear__py_cache(path):
    # 遍历目录下所有文件
    for file_name in os.listdir(path):
        abs_path = os.path.join(path, file_name)
        if file_name == "__pycache__":
            print(abs_path)
            # 删除 `__pycache__` 目录及其中的所有文件
            shutil.rmtree(abs_path)
        elif os.path.isdir(abs_path):
            # 递归调用
            clear__py_cache(abs_path)

if __name__ == '__main__': 
    delectFiles = []
    targetApi = "python"
    if len(sys.argv) >= 2:
        targetApi = sys.argv[1]
    
    clear_pbfile_dir()

    #加载配置文件
    with open('config.json') as j:
        print("====================加载配置文件====================")
        cfg = json.load(j)

    tabledir = os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg['tabledir'])

    #初始化文件
    print("====================初始化文件====================")
    delectFiles.append('pbfile/files.py')
    write_file_context(template.description())
    write_file_context(template.import_title())

    print("====================生成proto文件====================")

    fileNameToKey = {}
    for fileName in os.listdir(tabledir):
        with open(os.path.join(tabledir, fileName), 'r', encoding='gbk') as f:
            lines = f.readlines()
            if generate_proto(fileName, lines) == False:
                sys.exit()

    if targetApi == "python":
        exec("import pbfile.files as handleContext")

        print("====================序列化表格数据====================")
        for fileName in os.listdir(tabledir):
            with open(os.path.join(tabledir, fileName), 'r', encoding='gbk') as f:
                reader = csv.reader(f)
                datas = []
                for row in reader:
                    datas.append(row)
                generate_data(fileName, datas)

        print("====================清理临时文件====================")
        for deletePath in delectFiles:
            os.remove(deletePath)


    #清理临时目录
    protodir = os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg['protodir'])
    if os.path.exists(protodir):
        shutil.rmtree(protodir)  

    #清理pycache
    clear__py_cache(os.getcwd())