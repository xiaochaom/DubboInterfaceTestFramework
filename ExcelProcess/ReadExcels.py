# coding:utf-8
"""
Author:姚军
Date:20161102
"""
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import xlrd


class ReadExcels(object):
    """Excel测试用例表格处理
    处理传入的Excel表格，转换成测试用例List
    获取excel数据并返回一个list，list包含N个dict，每个dict保存用例Excel中的各个值。规则如下：
    用例编号	   名称	  描述	  系统	  服务	  方法	  参数	  预期结果	  数据初始化	   数据恢复       返回结果    (Excel列名)
    case_id    name   desc    system  service method  params  expect      data_init    data_recover  return_msg  (dict的key)
    :param filepath: excel case文件的路径
    :param case_line_list: 所要执行的case所在excel的行号,为数字.若未传入此参数，返回整个Excel数据，若参数传入且不为空，只返回列表中的行数的case信息
    :return: case_list: list包含N个dict，每个dict保存用例Excel中的各个值
    :param startLine: 取范围数据是的起始行
    :param endLine: 取范围数据是的结束行
    """
    '''get_case_list()
    对外开放调用的函数,处理批量用例excel文件
    '''

    def get_case_list(self, filePath, case_line_list=[], startLine=0, endLine=0):

        # TODO 字段数值跟最新设计不符合，需要增加数据初始化和恢复
        # TODO 需要根据传入的参数进行判断是获取整个excel还是获取列表里面的指定用例
        if len(case_line_list) == 0 and startLine > 0 and endLine > 0 and len(filePath) > 0:
            case_list = self.__get_by_value(filePath, startLine, endLine)
            return case_list
        elif len(case_line_list) >= 0 and startLine == 0 and startLine == 0 and len(filePath) > 0:
            case_list = self.__get_by_xlrd(filePath, case_line_list)
            return case_list
        else:
            raise ValueError('参数错误')

    @staticmethod
    def __open_excel(filePath=[]):
        data_list = []
        for i in range(0, len(filePath)):
            path = filePath[i]
            try:
                data = xlrd.open_workbook(path)
                data_list.append(data)
            except IOError, e:
                print str(e)
        return data_list

    def __get_by_xlrd(self, filePath, case_line_list=[]):
        datalist = self.__open_excel(filePath)
        print "LEN %d" % len(case_line_list)
        case_all_list = []
        for a in range(0, len(datalist)):
            table = datalist[a].sheets()[0]
            nrows = table.nrows
            print "NROWS:%d" % nrows
            case_line_list = len(case_line_list) == 0 and [i for i in range(1, nrows)] or [i for i in case_line_list]
            print "CaseLINE:%s" % case_line_list
            case_list = []
            for row_num in case_line_list:
                row_values = table.row_values(row_num)
                tmpCase = {'case_id': row_values[0].encode('utf8'), 'name': row_values[1].encode('utf8'),
                           'desc': row_values[2].encode('utf8'),
                           'system': row_values[3].encode('utf8').replace("\n", ""),
                           'service': row_values[4].encode('utf8').replace("\n", ""),
                           'method': row_values[5].encode('utf8').replace("\n", ""),
                           'data_init': row_values[6].encode('utf8').replace("\n", ""),
                           'data_recover': row_values[7].encode('utf8').replace("\n", ""),
                           'params': row_values[8].encode('utf8').replace("\n", ""),
                           'expect': row_values[9].encode('utf8').replace("\n", "")}
                case_list.append(tmpCase)
            case_all_list.append(case_list)
        return case_all_list

    def __get_by_value(self, filePath, startLine, endLine):

        datalist = self.__open_excel(filePath)
        case_all_list = []
        for a in range(0, len(datalist)):
            table = datalist[a].sheets()[0]
            nrows = table.nrows
            print nrows
            case_list = []
            if startLine < endLine:
                for row_num in range(startLine - 1, endLine):
                    row_values = table.row_values(row_num)
                    tmpCase = {'case_id': row_values[0].encode('utf8'), 'name': row_values[1].encode('utf8'),
                               'desc': row_values[2].encode('utf8'),
                               'system': row_values[3].encode('utf8').replace("\n", ""),
                               'service': row_values[4].encode('utf8').replace("\n", ""),
                               'method': row_values[5].encode('utf8').replace("\n", ""),
                               'data_init': row_values[6].encode('utf8').replace("\n", ""),
                               'data_recover': row_values[7].encode('utf8').replace("\n", ""),
                               'params': row_values[8].encode('utf8').replace("\n", ""),
                               'expect': row_values[9].encode('utf8').replace("\n", "")}
                    case_list.append(tmpCase)
            elif startLine > endLine:
                for row_num in range(endLine - 1, startLine - 1):
                    row_values = table.row_values(row_num)
                    tmpCase = {'case_id': row_values[0].encode('utf8'), 'name': row_values[1].encode('utf8'),
                               'desc': row_values[2].encode('utf8'),
                               'system': row_values[3].encode('utf8').replace("\n", ""),
                               'service': row_values[4].encode('utf8').replace("\n", ""),
                               'method': row_values[5].encode('utf8').replace("\n", ""),
                               'data_init': row_values[6].encode('utf8').replace("\n", ""),
                               'data_recover': row_values[7].encode('utf8').replace("\n", ""),
                               'params': row_values[8].encode('utf8').replace("\n", ""),
                               'expect': row_values[9].encode('utf8').replace("\n", "")}
                    case_list.append(tmpCase)
            else:
                row_values = table.row_values(startLine)
                tmpCase = {'case_id': row_values[0].encode('utf8'), 'name': row_values[1].encode('utf8'),
                           'desc': row_values[2].encode('utf8'),
                           'system': row_values[3].encode('utf8').replace("\n", ""),
                           'service': row_values[4].encode('utf8').replace("\n", ""),
                           'method': row_values[5].encode('utf8').replace("\n", ""),
                           'data_init': row_values[6].encode('utf8').replace("\n", ""),
                           'data_recover': row_values[7].encode('utf8').replace("\n", ""),
                           'params': row_values[8].encode('utf8').replace("\n", ""),
                           'expect': row_values[9].encode('utf8').replace("\n", "")}
                case_list.append(tmpCase)
            case_all_list.append(case_list)
        return case_all_list


if __name__ == "__main__":
    excelProcess = ReadExcels()
    try:
        tables = excelProcess.get_case_list(['E:\\DubboInterfaceTestFramework\\Testcases\\TestcaseTemplate.xlsx',
                                             'E:\\DubboInterfaceTestFramework\\Testcases\\TestcaseTemplate.xlsx'],
                                            [3, 5])
        for row in tables:
            # print json.dumps(row[u'\u53c2\u6570'])
            print row
    except Exception, e:
        print str(e)
