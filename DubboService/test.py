# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""
import sys,logging,re,random,datetime,chardet, json, time
from urllib import quote
from urllib import unquote
import base64,redis
from ServiceTool import ServiceTool

reload(sys)
sys.setdefaultencoding('utf8')




if __name__ == "__main__":
    # stringList = """[{"key1":"1"},{},{}]"""
    # s2 = u"{'aaa':'aa'}"
    # s3 = "[1,2,3,4]"
    # loadDict = json.loads(stringList)
    # print len(loadDict)
    print ServiceTool.get_google_auth_code("OKDTHXEIVIDSJXXW")
    print ServiceTool.get_google_auth_code("T6DM2D7MGOMULHK7")