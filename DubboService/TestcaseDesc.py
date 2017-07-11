# -*- coding: utf-8 -*-
import sys,re,time,types
sys.path.append("..")
import requests # python处理http相关的类库
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..")
import json,logging
from Config import Const

u'''
描述：用例描述对象
作者：王吉亮
日期：2017年5月5日
'''
class TestcaseDesc(object):
    def __init__(self):
        self.id = 0
        self.caseId = ''
        self.name = ''
        self.desc = ''
        self.stepCount = 0
        self.systems = ''
        self.addBy = ''
        self.modBy = ''
        self.addTime = '0000-00-00 00:00:00'
        self.modTime = '0000-00-00 00:00:00'
        self.initTakeTime = 0.0
        self.recoverTakeTime = 0.0
        self.execTakeTime = 0.0
        self.totalTakeTime = 0.0

        self.assert_msg = u"未进行断言"  # 初始化
        self.return_msg = u"未返回实际结果"  # 初始化
        self.test_result = Const.NOT_RUN  # 初始化
        self.perform_time = "null"

    def setError(self,errMsg):
        # logging.info(u"DubboService.py: execute_testcases: %s" % err_msg)
        self.return_msg = errMsg.encode('utf8')
        self.perform_time = "null"
        self.test_result = Const.ERROR
        self.assert_msg = self.return_msg

    def setFail(self,return_msg, assert_msg,perform_time):
        # logging.info(u"DubboService.py: execute_testcases: %s" % err_msg)
        self.return_msg = return_msg
        self.perform_time = perform_time
        self.test_result = Const.FAIL
        self.assert_msg = assert_msg

    def setPass(self,return_msg, assert_msg,perform_time):
        # logging.info(u"DubboService.py: execute_testcases: %s" % err_msg)
        self.return_msg = return_msg
        self.perform_time = perform_time
        self.test_result = Const.PASS
        self.assert_msg = assert_msg

    def toString(self):
        return """caseId = %s
title = %s
desc = %s
addBy = %s
modBy = %s
addTime = %s
modTime = %s
initTakeTime = %f
recoverTakeTime = %f
execTakeTime = %f
totalTakeTime = %f
assert_msg = %s
return_msg = %s
test_result = %s
perform_time = %s
""" % (self.caseId,self.name,self.desc,self.addBy,self.modBy,self.addTime,self.modTime,self.initTakeTime,self.recoverTakeTime,self.execTakeTime,self.totalTakeTime,
       self.assert_msg,self.return_msg,self.test_result,self.perform_time)