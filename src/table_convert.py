#coding=utf-8

#python版本：3.10.1以上
#请安装python环境，https://www.python.org/downloads/

#protobuf版本：4.21.6
#如无pb环境，在cmd命令行中执行下列信息：
#pip install protobuf==4.21.6

#version=1.0.2
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
    if type == 'Int':
        return 'int32'
    elif type == 'Bool':
        return 'bool'
    elif type == 'Float':
        return 'float'
    elif type == 'String':
        return 'bytes'    
    else:
        print("配置中填写了一个未知的数据类型%s", type)

    return ''

def  create_data_tuple(datas, datatypes):
    tuple = ()
    for index, type in enumerate(datatypes):
        if type == 'Int':
            tuple += (int(datas[index]),)
        elif type == 'Bool':
            tuple += ((True if int(datas[index]) == 1 else False),)
        elif type == 'Float':
            tuple += (float(datas[index]),)
        elif type == 'String':
            tuple += (bytes(datas[index], encoding='UTF-8'),)
        else:
            print("配置中填写了一个未知的数据类型%s", type)
    
    return tuple

def generate_data(fileName, datas):
    dataType = datas[Define.TableLineType.DataType.value]
    #生成pbscript并塞入表格数据
    key = fileNameToKey[fileName]
    if key != None:
        keyindex = 0
    tuplelist = []
    for index, data in  enumerate(datas):
        if index < Define.TableLineType.Max.value:
            continue

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
                    findcolumn = DataColumn.DataColumn(index, newname)
                    allColumns.append(findcolumn)
                else:
                    findcolumn.updatelist(index, newindex)
        else:
            allColumns.append(DataColumn.DataColumn(index, name))

    return allColumns

def generate_proto(fileName, lines):
    if len(lines) < Define.TableLineType.Max.value:
        print("表头行数少于3行，请检查表配置（标题，类型，cs类型）")
        return
    
    dataName = lines[Define.TableLineType.DataName.value].replace('\n', '').split(',')
    dataType = lines[Define.TableLineType.DataType.value].replace('\n', '').split(',')
    csType = lines[Define.TableLineType.CSType.value].replace('\n', '').split(',')

    descriptions = lines[Define.TableLineType.Description.value].replace('\n', '').split(',')[0].split(';')
    key = descriptions[0].split('=')[1]
    if key != dataName[0]:
        print("表格key值不对应，请检查表格是否配置了key值对应字段名，及是否名称相同.")
        return

    fileNameToKey[fileName] = key
    keyType = dataType[0]
    if len(dataName) != len(dataType) != len(csType):
        print("表头列数量不一致，请检查配置")
        return
    
    allColumns = parse_dataname(dataName)

    #生成pb格式
    protoName = fileName.replace('.csv', '.proto')
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

        #解析表头生成struct
        structName = protoName.replace('.proto','Struct')
        str += 'message '
        str += '{}{}\n'.format(structName,'{')
        for index, c in enumerate(allColumns):
            t = dataType[c.startIndex]
            cst = csType[c.startIndex]
            str += " repeated " if c.datalength > 1 else " optional "
            str += get_type_desc(t)
            str += ' '
            str += c.name.title()
            str += ' = {};\n'.format(index + 1)           
        str += '}\n'
        str += '\n'

        #生成包含struct的数据格式
        title = '%s%s\n' % ((protoName.replace('.proto',''),'{'))
        str += 'message '
        str += title.title()
        str += ' map<%s, %s> %s = 1;\n' % (get_type_desc(keyType), structName, structName)
        str += '}\n'
        file.write(str)
    
    write_file_context(template.import_pb2(fileName))
    write_file_context(template.serialize2db_message(fileName, protoName.replace('.proto','').title(), structName, allColumns))

    rootpath = os.path.dirname(os.path.abspath(__file__))
    compiler = os.path.join(rootpath, cfg['protocompiler'])

    protoName = fileName.replace('.csv', '.proto')
    protodir = os.path.join(rootpath, cfg['protodir'])
    dir = '%sdir' % (targetApi)
    tmpdir = os.path.join(rootpath, cfg[dir])
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)

    command = '%s\protoc -I=%s --%s_out=%s %s\%s' %(compiler, protodir, targetApi, tmpdir, protodir, protoName)
    os.system(command)
    print(command)

    delectFiles.append('pbfile/%s_pb2.py' %(fileName.replace('.csv', '')))
#

def clear_pbfile_dir():
    for fileName in os.listdir('pbfile'):
        if fileName.find('pb2') >= 0:
            os.remove(os.path.join('pbfile', fileName))

        if fileName.find('files') >=0:
            os.remove(os.path.join('pbfile', fileName))

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
            generate_proto(fileName, lines)


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