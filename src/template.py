def description():
    return '# Generated by tools.  DO NOT EDIT!\n\
# you can change template description in template.py'

def import_title():
    return 'import os'

def import_pb2(fileName):
    return 'import pbfile.%s_pb2' % (fileName.replace('.csv', ''))

def serialize2db_message(fileName, messageName, structName, allColumns):
    flieNameWithoutExt = fileName.replace('.csv', '')
    body = ""
    for index, column in enumerate(allColumns):
        if column.ignore:
            continue

        if column.datalength > 1:
            for i in range(column.datalength):
                body += "            obj.%s.append(tuple[%s])" % (column.name.title(), column.startIndex + i)
                body += "\n"
        else:
            body += "            obj.%s = tuple[%s]" % (column.name.title(), column.startIndex)
            body += "\n"
    return "\n\
def serialize2pb%s(keyindex, tuplelist, cfg):\n\
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', cfg['datadir'])\n\
    with open(os.path.join(datadir, '%s'), 'wb') as f:\n\
        inst = pbfile.%s_pb2.%s()\n\
        for tuple in tuplelist:\n\
            obj = inst.%s.get_or_create(tuple[keyindex])\n\
%s\n\
        f.write(inst.SerializeToString())\n" % (flieNameWithoutExt, fileName.replace('.csv', '.dat'), flieNameWithoutExt, messageName, structName, body)
