import os
import template_csharp

if __name__ == '__main__':
    csharppath = "..\\csharp"
    csharpdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), csharppath)

    csvpath = "..\\csv"
    csvpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), csvpath)
    print("====================生成读表器====================")
    names = []
    for fileName in os.listdir(csvpath):
        n = fileName.replace('.csv', '')
        names.append(n)

    with open(os.path.join(csharpdir, 'TabDef.cs'), 'w') as fileContext:
        fileContext.write(template_csharp.tab_class(names))

    with open(os.path.join(csharpdir, 'TabMgr.cs'), 'w') as fileContext:
        fileContext.write(template_csharp.tab_mgr(names))