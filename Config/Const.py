# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""

import sys, os,platform
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

#用例类型
TESTCASE_TYPE_GROUP = "GROUP"  #组合用例
TESTCASE_TYPE_INTERFACE = "INTERFACE"  #接口用例

#测试结果
NOT_RUN = "NOTRUN"
PASS = "PASS"
FAIL = "FAIL"
ERROR = "ERROR"

#数据初始化回复默认值
DATA_DEFAULT = "default"

#HTTP请求方式
POST = "post"
GET = "get"

#HOST KYES
SUPPORT_CONSOLE_URI = "supportconsoleuri"  #测试系统 支撑平台
PC_DISTRIBUTE_URI = "pcdistributeuri" # PC分销端
APPAPI_URI = "appapiuri" #APPAPI
WEIDIAN_URI = "weidianuri" #微店
SAAS_URI = "saasuri" #SAAS平台
SETTLEMENT_URI = "settlementuri" #清结算系统