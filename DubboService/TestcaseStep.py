# -*- coding: utf-8 -*-
import sys,re,time,types
sys.path.append("..")
import requests # python处理http相关的类库
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..")
import json,logging
from Config.Const import *

u'''
描述：用例步骤对象
作者：王吉亮
日期：2017年5月5日
'''
class TestcaseStep(object):
    def __init__(self):
        self.id = 0
        self.caseId = ''
        self.step = 0
        self.name = ''
        self.desc = ''
        self.system = ''
        self.service = ''
        self.method = ''
        self.data_init = DATA_DEFAULT
        self.data_recover = DATA_DEFAULT
        self.params = ''
        self.expect = ''
        self.varsconf = ''

        self.addBy = ''
        self.modBy = ''
        self.addTime = '0000-00-00 00:00:00'
        self.modTime = '0000-00-00 00:00:00'

        self.host = '0.0.0.0'
        self.port = 8888
        self.invoke_cmd = "No command executed!"
        self.initTakeTime = 0.0
        self.recoverTakeTime = 0.0
        self.execTakeTime = 0.0
        self.totalTakeTime = 0.0

        self.assert_msg = u"未进行断言"  # 初始化
        self.return_msg = u"未返回实际结果"  # 初始化
        self.test_result = NOT_RUN  # 初始化
        self.perform_time = "null"

    def setError(self,errMsg):
        # logging.info(u"DubboService.py: execute_testcases: %s" % err_msg)
        self.return_msg = errMsg.encode('utf8')
        self.perform_time = "null"
        self.test_result = ERROR
        self.assert_msg = self.return_msg

    def setFail(self,return_msg, assert_msg,perform_time):
        # logging.info(u"DubboService.py: execute_testcases: %s" % err_msg)
        self.return_msg = return_msg
        self.perform_time = perform_time
        self.test_result = FAIL
        self.assert_msg = assert_msg

    def setPass(self,return_msg, assert_msg,perform_time):
        # logging.info(u"DubboService.py: execute_testcases: %s" % err_msg)
        self.return_msg = return_msg
        self.perform_time = perform_time
        self.test_result = PASS
        self.assert_msg = assert_msg

    def toString(self):
        return """caseId = %s
step = %d
name = %s
desc = %s
system = %s
service = %s
method = %s
data_init = %s
data_recover = %s
params = %s
expect = %s
varsconf = %s
addBy = %s
modBy = %s
addTime = %s
modTime = %s
host = %s
port = %d
invoke_cmd = %s
initTakeTime = %f
recoverTakeTime = %f
execTakeTime = %f
totalTakeTime = %f
assert_msg = %s
return_msg = %s
test_result = %s
perform_time = %s
""" % (self.caseId,self.step,self.name,self.desc,self.system,self.service,self.method,self.data_init,self.data_recover,self.params,self.expect,self.varsconf,
       self.addBy,self.modBy,self.addTime,self.modTime,self.host,self.port,self.invoke_cmd,self.initTakeTime,self.recoverTakeTime,self.execTakeTime,self.totalTakeTime,self.assert_msg,
       self.return_msg,self.test_result,self.perform_time)
