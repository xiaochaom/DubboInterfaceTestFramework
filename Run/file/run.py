# coding:utf-8
"""
Author:王吉亮
Date:20161027
comments: 待废弃，独立于平台的执行excel的程序。对外公开使用web平台。
"""

import sys, os,logging

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

from time import time


from Lib.UsualTools import UsualTools
from Lib.runfunc import *
import chardet
from Config.EncodeConf import MyEncode

if __name__ == "__main__":
    time_run_start = time()
    try:
        sysparam = sys.argv[1]
        if sysparam.strip()=="-h" or sysparam.strip()=="-help" or sysparam.strip()=="help" or sysparam.strip()=="h":
            print u"""参数间用--分隔，首尾不用，如下：
protocol=HTTP--file=Testcases/Testcases_http.xlsx--conf=test--loglevel=DEBUG

各个参数详解：
protocol=HTTP #协议，目前支持HTTP和DUBBO
file=Testcases/Testcases_http.xlsx #要测试的用例文件或者文件路径，多个文件用英文半角逗号隔开
case_line_list=2,4,5to12 #执行用例文件中的特定行用例，2为最小行。多行之间用英文半角逗号隔开，连续行之间可以用5to12方式表示5到12行，包含5和12行
conf=test #测试环境：test 或者 dev
loglevel=DEBUG #log级别：INFO 或者 DEBUG
logfile=logs/logginglogHTTP.log #log文件地址
is_send_mail=NO #是否发送邮件给开发，开发邮箱在配置文件中。YES或者NO
mail_list=wangjiliang@mftour.cn,wanjiliang@163.com #接收报告的邮件地址，多个邮箱中间用英文半角逗号隔开
report_path=reports #本地存放报告的路径
report_filename=ReportTestcases_http.xlsxHTTPtest.html #报告文件名
confpath=/home/InterfaceFrameworkOnline #Config目录的父目录路径
"""
            sys.exit()

        print sysparam
        #sysparam.decode(MyEncode().os_encoding)
        param_dict = chardet.detect(sysparam)['encoding'] == 'ascii' and init_sys_argv(sysparam.decode('ascii')) or init_sys_argv(sysparam.decode(MyEncode().os_encoding))
        print param_dict
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: main: 没有参数:%s" % e
        param_dict = init_sys_argv("protocol=DUBBO--file=TestcasesForDubbo/--report_path=reports--conf=test;loglevel=DEBUG--logfile=test.log".decode('ascii'))

    processed_param_dict = process_init_param_dict(param_dict)
    print UsualTools().get_current_time() + u"=>run.py: main: 配置dict:%s" % processed_param_dict
    print UsualTools().get_current_time() + u"=>run.py: main: Config conf_dict:%s" % processed_param_dict['conf'].conf_dict

    for k in processed_param_dict.keys():
        print UsualTools().get_current_time() + u"=>run.py: main: 配置:%s:%s" % (k, processed_param_dict[k])

    print processed_param_dict
    #根据PARAM设定输出log的级别和保存文件。
    logging.basicConfig(level=processed_param_dict['loglevel'],
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=processed_param_dict['logfile'],
                        filemode='w')
    logging.debug(processed_param_dict)
    proto = processed_param_dict['protocol']
    is_send_mail = processed_param_dict['is_send_mail'] == "YES" and True or False
    mail_list = processed_param_dict['mail_list']

    if proto == "DUBBO":
        logging.info(u"本次测试为DUBBO接口测试。")
        if type(processed_param_dict['file']) == type([]):
            # 是个list,说明是多文件，那么执行suite 或者 cases
            if len(processed_param_dict['file']) == 1 and len(processed_param_dict['case_line_list']) > 0:
                # filelist长度为1，那么就是单文件，并且caselist大于0，页就是不为空，那么要执行cases
                run_cases(processed_param_dict['file'][0],processed_param_dict)
            else:
                # 否则执行suites
                run_suites(processed_param_dict['file'],processed_param_dict)
        else:
            # 是个string，那么就是目录，调用runall
            run_all(processed_param_dict['file'], processed_param_dict)
    elif proto == "HTTP":
        logging.info(u"本次测试为HTTP接口测试。")
        if type(processed_param_dict['file']) == type([]):
            # 是个list,说明是多文件，那么执行suite 或者 cases
            if len(processed_param_dict['file']) == 1 and len(processed_param_dict['case_line_list']) > 0:
                # filelist长度为1，那么就是单文件，并且caselist大于0，页就是不为空，那么要执行cases
                run_http_cases(processed_param_dict['file'][0],processed_param_dict)
            else:
                # 否则执行suites
                run_http_suites(processed_param_dict['file'],processed_param_dict)
        else:
            run_http_all(processed_param_dict['file'], processed_param_dict)
    else:
        print u"错误的协议，请确认传入的protocol参数为DUBBO或者HTTP协议。"

    time_run_end = time()
    logging.info( UsualTools().get_current_time() + u"=>run.py: main: 本次测试总时间: %s秒 " % (time_run_end - time_run_start) )
