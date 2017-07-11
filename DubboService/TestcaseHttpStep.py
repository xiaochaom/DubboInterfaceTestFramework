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
class TestcaseHttpStep(object):
    def __init__(self):
        self.id = 0
        self.caseId = ''
        self.stepId = 0
        self.name = ''
        self.desc = ''

        self.protocol = 'http' #默认http，可能还有https
        self.host = '' #根据hostkey获取host，或者根据用户输入获取host
        self.method = '' #post or get
        self.header = '' #hearder json格式 {"token":"KLJL#LKJLK23LKJ"}
        self.url = '' #"/appapi/user/login"  /saas/user/login /supportConsle/user 等等
        self.params = '' #data=adskjfas&sign=asdfklasdf  k1=v1&k2=v2的字符串形式传递
        self.data_init = DATA_DEFAULT  #sql组合，中间用;间隔。
        self.data_recover = DATA_DEFAULT
        self.expect = ''
        self.varsconf = '' #请求前的变量集合
        self.varsconf_result = ''#请求后根据返回结果生成的变量集合，或者请求后从db查询的数据做变量的结果集合。

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
        self.test_result = NOT_RUN  # 初始化
        self.perform_time = "null"

    def copy (self,newStep):
        self.id = newStep.id
        self.caseId = newStep.caseId
        self.stepId = int(newStep.stepId)
        self.name = newStep.name
        self.desc = newStep.desc
        self.protocol = newStep.protocol
        self.host = newStep.host
        self.method = newStep.method
        self.header = newStep.header
        self.url = newStep.url
        self.params = newStep.params
        self.data_init = newStep.data_init
        self.data_recover = newStep.data_recover
        self.expect = newStep.expect
        self.varsconf = newStep.varsconf
        self.varsconf_result = newStep.varsconf_result
        self.addBy = newStep.addBy
        self.modBy = newStep.modBy
        self.addTime = newStep.addTime
        self.modTime = newStep.modTime
        self.initTakeTime = newStep.initTakeTime
        self.recoverTakeTime = newStep.recoverTakeTime
        self.execTakeTime = newStep.execTakeTime
        self.totalTakeTime = newStep.totalTakeTime
        self.assert_msg = newStep.assert_msg
        self.return_msg = newStep.return_msg
        self.test_result = newStep.test_result
        self.perform_time = newStep.perform_time

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
        return """self.id = %d
self.caseId = %s
self.stepId = %d
self.name = %s
self.desc = %s
self.protocol = %s
self.host = %s
self.method = %s
self.header = %s
self.url = %s
self.params = %s
self.data_init = %s
self.data_recover = %s
self.expect = %s
self.varsconf = %s
self.varsconf_result = %s
self.addBy = %s
self.modBy = %s
self.addTime = %s
self.modTime = %s
self.initTakeTime = %f
self.recoverTakeTime = %f
self.execTakeTime = %f
self.totalTakeTime = %f
self.assert_msg = %s
self.return_msg = %s
self.test_result = %s
self.perform_time = %s
""" % (self.id,self.caseId,self.stepId,self.name,self.desc,self.protocol,self.host,self.method,self.header,self.url,self.params,self.data_init,self.data_recover,
       self.expect,self.varsconf,self.varsconf_result,self.addBy,self.modBy,self.addTime,self.modTime,self.initTakeTime,self.recoverTakeTime,self.execTakeTime,self.totalTakeTime,
       self.assert_msg,self.return_msg,self.test_result,self.perform_time)
