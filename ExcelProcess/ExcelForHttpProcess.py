# coding:utf-8
"""
Author:姚军
Date:20161027
"""
import json
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import xlrd


class ExcelForHttpProcess(object):
    """get_case_list()
    对外开放调用的函数
    """

    def get_case_list(self, filePath, case_line_list=[], startLine=0, endLine=0):
        """Excel测试用例表格处理
        处理传入的Excel表格，转换成测试用例List
        获取excel数据并返回一个list，list包含N个dict，每个dict保存用例Excel中的各个值。规则如下：
         [  "用例编号", "名称",   "描述", "数据初始化", "数据恢复",  "HTTP请求头信息" , "接口","参数", "预期结果", "变量配置"]   (Excel列名)
            case_id      name     desc     data_init    data_recover  header            url     params  expect      varsconf  (dict的key)
        :param filePath: excel case文件的路径
        :param case_line_list: 所要执行的case所在excel的行号,为数字.若未传入此参数，返回整个Excel数据，若参数传入且不为空，只返回列表中的行数的case信息
        :return: case_list: list包含N个dict，每个dict保存用例Excel中的各个值
        :param startLine: 取范围数据是的起始行
        :param endLine: 取范围数据是的结束行
        """
        if len(case_line_list) == 0 and startLine > 0 and endLine > 0:
            case_list = self.__get_by_value(filePath, startLine, endLine)
            return case_list
        elif len(case_line_list) >= 0 and startLine == 0 and startLine == 0:
            case_list = self.__get_by_xlrd(filePath, case_line_list)
            return case_list
        else:
            raise ValueError(u'ExcelForHttpProcess.py: get_case_list: 传入参数错误'.encode('utf8'))

    def __get_by_xlrd(self, filePath, case_line_list, by_index=0):
        data = self.__open_excel(filePath)
        try:
            table = data.sheets()[by_index]
        except Exception:
            raise IOError(u"ExcelForHttpProcess.py: __get_by_xlrd: data.sheets()[by_index]: by_index长度超过excel中的长度".encode('utf8'))
        nrows = table.nrows
        result = self.__repeat(table, nrows)
        if len(result) > 0:
            raise Exception(u'ExcelForHttpProcess.py: __get_by_xlrd: 测试编号列中有重复元素,且重复元素为：%s' % json.dumps(result))

        # print u"ExcelProcess: __get_by_xlrd: NROWS:%d" % nrows
        # print u"ExcelProcess: __get_by_xlrd: LEN %d" % len(case_line_list)
        # print json.dumps(table.row_values(0), encoding='UTF-8', ensure_ascii=False)
        if json.dumps(table.row_values(0), encoding='UTF-8', ensure_ascii=False) == json.dumps(
                ["用例编号", "名称", "描述", "数据初始化", "数据恢复", "HTTP请求头信息", "接口", "参数", "预期结果", "变量配置"], encoding='UTF-8',
                ensure_ascii=False):
            for num in range(0, len(case_line_list)):
                if case_line_list[num] > nrows or case_line_list[num] <= 1:
                    raise ValueError(u'ExcelProcess: __get_by_xlrd: 传入的list集合中有行数大于Excel文件最大行数或行数小于1!'.encode('utf8'))

            case_line_list = len(case_line_list) == 0 and [i for i in range(1, nrows)] or [i - 1 for i in
                                                                                           case_line_list]
            # print u"ExcelProcess: __get_by_xlrd: CaseLINE:%s" % case_line_list
            case_list = []
            for row_num in case_line_list:
                row_values = table.row_values(row_num)
                if "[NOTRUN]" in row_values[1]: continue
                tmpCase = {'case_id': row_values[0].encode('utf8').replace("\n", "").strip(),
                           'name': row_values[1].encode('utf8'),
                           'desc': row_values[2].encode('utf8'),
                           'data_init': row_values[3].encode('utf8'),
                           'data_recover': row_values[4].encode('utf8'),
                           'header': row_values[5].encode('utf8'),
                           'url': row_values[6].encode('utf8').replace("\n", "").strip(),
                           'params': row_values[7].encode('utf8').replace("\n", "").strip(),
                           'expect': row_values[8].encode('utf8').strip(),
                           'varsconf': str(row_values[9]).encode('utf8').replace("\n", "").strip()}
                case_list.append(tmpCase)

            return case_list

        else:
            raise IOError(u'ExcelForHttpProcess.py: __get_by_xlrd: Excel表中的列名不正确或者顺序错误!'.encode('utf8'))

    def __get_by_value(self, filePath, startLine, endLine, by_index=0):
        data = self.__open_excel(filePath)
        table = data.sheets()[by_index]
        nrows = table.nrows
        result = self.__repeat(table, nrows)
        if len(result) > 0:
            raise Exception(u'ExcelForHttpProcess.py: __get_by_xlrd: 测试编号列中有重复元素,且重复元素为：%s' % json.dumps(result))
        # print u"ExcelProcess: __get_by_value: NROWS:%d" % nrows
        case_list = []

        def CaseList(Case):
            row_values = table.row_values(Case)
            tmpCase = {'case_id': row_values[0].encode('utf8').replace("\n", "").strip(),
                       'name': row_values[1].encode('utf8'),
                       'desc': row_values[2].encode('utf8'),
                       'data_init': row_values[3].encode('utf8'),
                       'data_recover': row_values[4].encode('utf8'),
                       'header': row_values[5].encode('utf8'),
                       'url': row_values[6].encode('utf8').replace("\n", "").strip(),
                       'params': row_values[7].encode('utf8').replace("\n", "").strip(),
                       'expect': row_values[8].encode('utf8').replace("\n", "").strip(),
                       'varsconf': str(row_values[9]).encode('utf8').replace("\n", "").strip()}
            return tmpCase

        if json.dumps(table.row_values(0), encoding='UTF-8', ensure_ascii=False) == json.dumps(
                ["用例编号", "名称", "描述", "数据初始化", "数据恢复","HTTP请求头信息" , "接口","参数", "预期结果", "变量配置"], encoding='UTF-8',
                ensure_ascii=False):
            if 1 < startLine < endLine < nrows:
                for row_num in range(startLine - 1, endLine):
                    case_list.append(CaseList(row_num))
            elif 1 < startLine < nrows < endLine:
                for row_num in range(startLine - 1, nrows):
                    case_list.append(CaseList(row_num))
            elif nrows > startLine > endLine > 1:
                for row_num in range(endLine - 1, startLine):
                    case_list.append(CaseList(row_num))
            elif startLine > nrows > endLine > 1:
                for row_num in range(endLine - 1, nrows):
                    case_list.append(CaseList(row_num))
            elif 1 < startLine == endLine < nrows:
                case_list.append(CaseList(startLine - 1))
            else:
                raise ValueError(u'ExcelForHttpProcess.py: __get_by_value: 传入数据的起始行大于Excel文件最大行数或起始行小于1!'.encode('utf8'))
            return case_list
        else:
            raise IOError(u'ExcelForHttpProcess.py: __get_by_value: Excel表中的列名不正确或者列名顺序错误!')

    @staticmethod
    def __open_excel(filePath):
        try:
            data = xlrd.open_workbook(filePath)
            return data
        except Exception:
            raise IOError(u"ExcelForHttpProcess.py: __open_excel: 解析文件异常请传入正确的Excel文件".encode('utf8'))

    @staticmethod
    def __repeat(table, nrows):
        dataCase = table.col_values(0)
        RepeatDataList = []
        for x in range(2, nrows):
            if dataCase[x - 1] == dataCase[x]:
                RepeatDataList.append(dataCase[x])
        return RepeatDataList


if __name__ == "__main__":
    excelProcess = ExcelForHttpProcess()
    try:
        tables = excelProcess.get_case_list('../Run/Testcases/Testcases_http.xlsx',[3,4])
        for row in tables:
            # print json.dumps(row[u'\u53c2\u6570'])
            print row
    except Exception, e:
        print str(e)