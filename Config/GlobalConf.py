# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""

import sys, os,platform
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

class ServiceConf(object):
    def __init__(self,env='test'):
        self.sql_effect_lines = 200
        self.framework_version = 'Interface Test 2.0'

        # self.db = {}
        self.dbhost = '10.0.18.31'
        self.dbport = 3306
        self.dbusername = 'root'
        self.dbpassword = 'mfpzj123'
        self.dbname = env == 'test' and 'test_platform' or "test_platform_release"

        #谷歌身份验证器密钥
        self.GOOGLE_AUTH_SETTLEMENT_TEST_KEY = "OKDTHXEIVIDSJXXW"
        self.GOOGLE_AUTH_SETTLEMENT_DEV_KEY = "T6DM2D7MGOMULHK7"

        if self._isWindowsSystem():
            self.base_path = "D:/devcodes/DubboInterfaceTestFramework"  #IMP: 必须的，获取db配置文件所需要的。
        elif self._isLinuxSystem():
            self.base_path = "/home/InterfaceFrameworkOnline"    #IMP: 必须的，获取db配置文件所需要的。
        else:
            self.base_path = "/Users/liyachao/PycharmProjects/DubboInterfaceTestFramework" #IMP: 必须的，获取db配置文件所需要的。

    def _isWindowsSystem(self):
        return 'Windows' in platform.system()

    def _isLinuxSystem(self):
        return 'Linux' in platform.system()


