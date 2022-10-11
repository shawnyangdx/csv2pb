@echo off

echo 开始生成C#代码
cd ./src
python table_convert.py csharp
echo 生成完毕！
pause