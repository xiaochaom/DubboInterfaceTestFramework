# -*- coding: utf-8 -*-
import xlrd
import sys

reload(sys)
sys.setdefaultencoding('utf8')


# 参数:file：Excel文件路径
def open_excel(file='E:\\DubboInterfaceTestFramework\\Testcases\\TestcaseTemplate.xlsx'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception, e:
        print str(e)


# 根据索引获取Excel表格中的数据  colnameindex：表头列名所在行的所以  ，by_index：表的索引
def excel_table_byindex(colnameindex=0, by_index=0):
    data = open_excel()
    table = data.sheets()[by_index]
    nrows = table.nrows  # 行数
    colnames = table.row_values(colnameindex)  # 某一行数据
    list = []
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            app = {}
            for i in range(len(colnames)):
                app[colnames[i]] = row[i]
            # list.append(json.dumps(app, encoding='UTF-8', ensure_ascii=False))
            list.append(app)
    return list


# 根据名称获取Excel表格中的数据   colnameindex：表头列名所在行的所以  ，by_name：Sheet1名称
def excel_table_byname(colnameindex=0, by_name=u'Sheet1'):
    data = open_excel()
    table = data.sheet_by_name(by_name)
    nrows = table.nrows  # 行数
    colnames = table.row_values(colnameindex)  # 某一行数据
    list = []
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            app = {}
            for i in range(len(colnames)):
                app[colnames[i]] = row[i]
            # list.append(json.dumps(app, encoding='UTF-8', ensure_ascii=False))
            list.append(app)
    return list


def main():
    tables = excel_table_byindex()
    for row in tables:
        # print json.dumps(row[u'\u53c2\u6570'])
        print row


if __name__ == "__main__":
    main()
