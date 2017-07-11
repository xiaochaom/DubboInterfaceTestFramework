# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""

import ConfigParser


class Config(object):
    """全局参数配置
    考虑使用配置文件
    """

    def __init__(self, confpath="test.conf"):
        cf = ConfigParser.ConfigParser()
        cf.read(confpath)
        self.conf_dict = {}
        self.sections = cf.sections()
        for section in self.sections:
            items = cf.items(section)
            self.conf_dict[section] = {}
            for item in items:
                self.conf_dict[section][item[0]] = item[1]

if __name__ == "__main__":
    print Config("test.conf").conf_dict
