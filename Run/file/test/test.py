# coding:utf-8
"""
Author:王吉亮
Date:20170117
"""
import logging
import logging.handlers
import sys,json

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

import datetime,time,logging

from DubboService.TestcaseGroup import TestcaseGroup
from DubboService.TestcaseDesc import TestcaseDesc
from DubboService.TestcaseStep import TestcaseStep
from DubboService.DubboService import DubboService
from Lib.DBTool import DBTool
from Lib.runWebPlatformFunc import *
from Lib.UsualTools import UsualTools
from Config.PromptMsg import PromptMsg

def replace_NOW_TIMESTAMP( params):
    find_start_tag = "NOW_TIMESTAMP()"
    find_end_tag = "D"
    nowplus_startpos = params.find(find_start_tag)  # 不存在是-1
    if nowplus_startpos == -1: return params
    # nowplus_endpos = params.find(find_end_tag, nowplus_startpos)  # 如果endpos没有那么就是只写当前日期
    # value_tobe_process = params[nowplus_startpos + len(find_start_tag):nowplus_endpos]
    sysnow = str(long(time.time()))  # ('%Y-%m-%d %H:%M:%S')
    print sysnow
    params_splited = params.split(find_start_tag)
    len_params_splited = len(params_splited)
    if len_params_splited == 1:  # 没有发现关键字 NOW()
        return params

    for i in range(0, len_params_splited - 1):
        Dpos = params_splited[i + 1].find(find_end_tag)
        if Dpos == -1:
            params_splited[i + 1] = sysnow + params_splited[i + 1]
        else:
            value_tobe_process = params_splited[i + 1][:Dpos]
            try:
                if value_tobe_process[0] == "+":
                    tobe_plus_value = int(value_tobe_process[1:])
                    tobe_day = long(time.time()) + long(24*3600)
                    params_splited[i + 1] = params_splited[i + 1].replace("+" + str(tobe_plus_value) + "D", tobe_day, 1)
                elif value_tobe_process[0] == "-":
                    tobe_plus_value = int(value_tobe_process[1:])
                    tobe_day = long(time.time()) - long(24*3600)
                    params_splited[i + 1] = params_splited[i + 1].replace("-" + str(tobe_plus_value) + "D", tobe_day, 1)
                else:
                    params_splited[i + 1] = sysnow + params_splited[i + 1]
            except Exception, e:
                params_splited[i + 1] = sysnow + params_splited[i + 1]
    new_params = ""
    for value in params_splited:
        new_params = new_params + value
    return new_params


def get_vars_by_varsconf(varsconf, env):
    logging.debug("##############1#############%s" % varsconf)
    varsconfstr = ""
    start_tag = "[CONF=common]"
    end_tag = "[ENDCONF]"
    find_start = varsconf.find(start_tag)
    logging.debug("##############2#############%s" % find_start)
    if find_start >= 0:
        find_end = varsconf.find(end_tag, find_start)
        logging.debug("##############2#############%s" % find_end)
        if find_end >= 0:
            varsconfstr = varsconfstr + varsconf[find_start + len(start_tag):find_end].strip()
            logging.debug("##############2#############%s" % varsconfstr)
    start_tag = "[CONF=%s]" % env
    end_tag = "[ENDCONF]"
    find_start = varsconf.find(start_tag)
    logging.debug("##############3#############%s" % find_start)
    if find_start >= 0:
        find_end = varsconf.find(end_tag, find_start)
        logging.debug("##############3#############%s" % find_end)
        if find_end >= 0:
            varsconfstr = varsconfstr + varsconf[find_start + len(start_tag):find_end].strip()
            logging.debug("##############3#############%s" % varsconfstr)
            logging.debug("##############3#############%s" % varsconfstr)
    logging.debug("##############4#############%s" % varsconfstr)
    return varsconfstr


import hmac, base64, struct, hashlib, time

def get_google_auth_code(secret, digest_mode=hashlib.sha1, intervals_no=None):
    if intervals_no == None:
        intervals_no = int(time.time()) // 30
    key = base64.b32decode(secret)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, digest_mode).digest()
    o = ord(h[19]) & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    while(len(str(h))<6):
        h = "0" + str(h)
    return h

if __name__ == '__main__':
    modules = "TestKeyword"
    obj = __import__(modules, fromlist=True)
    key = "key1"
    if hasattr(obj,key):
        func = getattr(obj,key)
        func()

    key = "key2"
    if hasattr(obj, key):
        func = getattr(obj, key)
        func("k1","v1")