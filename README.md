# Dubbo接口自动化测试框架V1.0

***
本文档为框架结构说明文档，请认真阅读
***

## 一 类、函数设计文档
***
ReadExcel.py提供excel解析功能
1. open_excel函数为读取excel文件内容

2. excel_table_byindex函数通过页索引来处理相应页数据并返回list集合

3. excel_table_byname函数通过页名字来处理相应页数据并返回list集合
***

***
### ExcelProcess.py文件中*`ExcelProcess`*类的*`get_case_list`*函数提供对外调用，其他函数不提供调用
>*`get_case_list`*函数入参数说明 1.如果传入startLine和endLine参数那么必须传入空list，2.如果传入空list可以选择是否传入
startLine和endLine参数
***

***
### ReadExcels.py文件中*`ReadExcels`*类的*`get_case_list`*函数提供对外调用实现批量处理excel文件，其他函数不提供外部调用
>特别注意点，需传入list集合的文件路径
***

***
### DubboService.py提供用例执行功能
>*`execute_testcases`*函数执行完测试用例后返回带测试结果的结果集合
***

***
### Config.py文件中的*`Config`*类为配置文件类
>dev.conf为开发环境配置文件，test.conf为测试环境配置文件
***

***
### ResultProcess.py文件中的*`ResultProcess`*类为结果处理类
>`assert_result`函数为断言处理函数
***

***
### DBTool.py文件中的*`DBTool`*类为数据库连接类
>
***


## 二、设计图
本自动化测试框架第一阶段设计流程如下：  
![第一阶段设计流程](https://raw.githubusercontent.com/DreamYa0/MarkdownPhotos/master/Frist.jpg)