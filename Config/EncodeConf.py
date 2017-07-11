# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""

import sys, os,platform

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

class MyEncode(object):
    def __init__(self):
        if self._isLinuxSystem():
            self.os_encoding = "gb2312"
        else:
            self.os_encoding = "gb18030"

        #self.telent_encoding = "gb2312"


    def _isWindowsSystem(self):
        return 'Windows' in platform.system()

    def _isLinuxSystem(self):
        return 'Linux' in platform.system()

