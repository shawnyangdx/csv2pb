csv2pb - 表格转protobuf工具
=====
一个轻量的转表工具，csv转protobuf。支持命令行导出多种语言。  

环境
=====
**python版本**：3.10.1以上,https://www.python.org/downloads/  
**protobuf版本**：4.21.6  
如无pb环境，在命令行中执行下列指令：
```py
pip install protobuf==4.21.6
```

目录
=====
├─`complier` protocol buffer compiler。官方地址：'https://developers.google.com/protocol-buffers/docs/downloads'  
├─`csv` 表格目录  
├─`data` 序列化数据，即表格二进制pb数据。后缀.dat  
├─`src` 源码(python)  
├─`Tools` 一些不同应用场景的工具集或环境

命令行
====
```py
python table_convert.py TARGET_API
```

注意配置好python的环境变量 ，并保证执行目录在src根目录  
**TARGET_API**: 编译pb语言类型。执行时会根据传人的命令行参数，编译对应的pb版本。并创建同名文件夹。
目前已支持的语言：  
https://developers.google.com/protocol-buffers/docs/pythontutorial

|  |
| :-----| 
| cpp | 
| csharp | 
| dart | 
| go | 
| python | 

表格配置相关
====
**例子：**（请参考csv目录下的Beginer.csv）
| 名称 | A | B | C |......|
| ----- | ---- | ---- | ---- | ---- | 
| 数据类型 |Int|Float |String|....|
| CSType |1|1|1|....| 
| 数据 | ....| ....| ....| ....| 
| .... | ....|....|....|....|

**名称**:  参数名称，在逻辑中调用。  根据名称配置不同生成列表等数据结构。  
**数据类型：**
| 基本类型 | 描述|
| -----|----| 
| Int |整形| 
| Float |浮点| 
| String | 字符串| 
| Bool | 波尔值|

**CSType：**
区分服务器客户端或共用，过滤无用字段。（目前还未实现）  
  
  
**其他**：
* 可以注释行，在行最开始使用<font color=red>'#'</font> 
* 可以注释列，在表头字段名称前使用<font color=red>'#'</font> 

ChangeLog
====
**v1.0.3:**
* 增加注释列，在表头字段前使用#
* client-server字段如果遗漏了配置，默认为"cs"，同时会给出提示
  
**v1.0.2:**
* 修改pb结构，repeated替换为map
* 表格结构修改，表头添加“描述”行，指定key值。
* client-server字段配置描述修改：改为更直观的"cs"
  
**v1.0.1:**
* 使用py内置csv模块，处理逗号问题
* 转表出现异常，在运行开始清理临时文件
* 序列化字符串为protobuf的bytes
