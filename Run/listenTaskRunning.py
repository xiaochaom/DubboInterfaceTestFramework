# coding:utf-8
"""
Author:王吉亮
Date:20170407
comments: 用例执行时取消的功能
"""

import sys, time, types, datetime, logging.handlers,os

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

from Lib.DBTool import DBTool
from Lib.runWebPlatformFunc import *
from Lib.UsualTools import UsualTools
from Config.PromptMsg import PromptMsg


def run_on_linux():
    import time
    logging.basicConfig(level=logging.DEBUG)  # 初始化logging
    #################################################################################################
    # 定义一个StreamHandler，将INFO级别或更高的志信息打印到标准错误，并将其添加到当前的日志处理对象#
    logger = logging.getLogger('')
    consoletmp = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    consoletmp.setFormatter(formatter)
    logger.addHandler(consoletmp)
    #################################################################################################
    # --log=INFO--webenv=test
    try:
        argDict = getArgsDict(sys.argv[1])
        try:
            logLevel = argDict['log'] == "INFO" and "INFO" or "DEBUG"
        except Exception, e:
            print "No param log, use default[DEBUG]!"
            logLevel = "DEBUG"

        try:
            testenv = argDict['webenv'] == "release" and "release" or "test"
        except Exception, e:
            print "No param webenv, use default[test]!"
            testenv = "test"

    except Exception, e:
        print "No args. Use default!"
        logLevel = 'DEBUG'
        testenv = 'test'

    if UsualTools.isWindowsSystem():
        print u"windows不能运行任务取消！"
    elif UsualTools.isMacOS():
        print u"macOS不能运行任务取消！"

    ##################################################################################################
    # 初始化数据库配置conf
    sc = ServiceConf(testenv)
    db = DBTool(sc.dbhost, sc.dbport, sc.dbusername, sc.dbpassword, sc.dbname)

    conf_path = ""
    if UsualTools.isLinuxSystem():  # 正式环境
        conf_path = "/home"
    elif UsualTools.isWindowsSystem():  # 王吉亮测试环境
        conf_path = "D:/devcodes/DubboInterfaceTestFramework/DubboInterfaceTestFramework"
    elif UsualTools.isMacOS():  # liyaochao测试环境
        conf_path = "/home"

    commonRetCode, commnonConfig = getConfFromDB(db, "commonconf", confPath=conf_path + "/taskCancelcommonconf.conf")
    commonDict = commnonConfig.conf_dict
    db.release()
    if commonRetCode['errorCode'] != '10000':
        print u"没有得到commonconf配置文件！"
        sys.exit(0);
    ##################################################################################################
    # IMP:不能用../定位的原因是在平台上要用绝对路径执行程序，用../定位不到配置文件，只能用绝对路径
    base_path = "D:/devcodes/DubboInterfaceTestFramework/DubboInterfaceTestFramework"
    if UsualTools.isLinuxSystem():
        base_path = commonDict['platform']['basepath']
    log_path = u"%s/logs" % base_path
    bin_path = u"%s/bin" % base_path
    print u"logPath:%s" % log_path
    print u"logLevel:%s" % logLevel
    print u"%s:%s" % (PromptMsg.loadLogPath, log_path)
    logFileName = '%s/%s.log' % (log_path, "listenTaskRunning")
    print u"logFileName:%s" % logFileName
    #################################################################################################
    # 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logLevel == "INFO" and logging.INFO or logging.DEBUG)
    # handler = logging.FileHandler(logFileName)
    handler = logging.handlers.RotatingFileHandler(logFileName, maxBytes=1024 * 1024 * 10, backupCount=5)  # 实例化handler
    logger.addHandler(handler)
    #################################################################################################
    logging.info(UsualTools().get_current_time() + (u"=>runPlatformTask.py: run_on_linux: logPath: %s " % log_path))
    logging.info(UsualTools().get_current_time() + (u"=>runPlatformTask.py: run_on_linux: logLevel: %s " % logLevel))
    webenvarg = "--webenv=release"
    logarg = "--log=INFO"

    sleep(2)
    taskName = "runCaseDebugTask"
    psCmd = "ps aux|grep -v 'grep'|grep -c '%s/%s %s'" %(bin_path,taskName,webenvarg)
    killCmd = "killall -9 %s" % taskName
    startCmd = "%s/%s %s%s >%s/%sPrint.log 2>&1 &" % (bin_path,taskName,webenvarg,logarg,log_path,taskName)
    psCmdOut = os.popen(psCmd).readlines()
    processCount = int(psCmdOut[0].strip())
    if processCount == 2 :
        logging.info( u"进程[%s]数量[%d],任务状态正常。" % (taskName,processCount))
    else :
        logging.info( u"进程[%s]数量[%d],进程数量不等于预期[2]，执行重启命令。" % (taskName, processCount))
        os.system(killCmd)
        sleep(1)
        os.system(startCmd)
        logging.info(u"进程[%s]启动完成。" % taskName)

    sleep(2)
    taskName = "runPlatformTask"
    psCmd = "ps aux|grep -v 'grep'|grep -c '%s/%s %s'" %(bin_path,taskName,webenvarg)
    killCmd = "killall -9 %s" % taskName
    startCmd = "%s/%s %s%s >%s/%sPrint.log 2>&1 &" % (bin_path,taskName,webenvarg,logarg,log_path,taskName)
    psCmdOut = os.popen(psCmd).readlines()
    processCount = int(psCmdOut[0].strip())
    if processCount == 2 :
        logging.info( u"进程[%s]数量[%d],任务状态正常。" % (taskName,processCount))
    else :
        logging.info( u"进程[%s]数量[%d],进程数量不等于预期[2]，执行重启命令。" % (taskName, processCount))
        os.system(killCmd)
        sleep(1)
        os.system(startCmd)
        logging.info(u"进程[%s]启动完成。" % taskName)

    sleep(2)
    taskName = "runTaskCancel"
    psCmd = "ps aux|grep -v 'grep'|grep -c '%s/%s %s'" %(bin_path,taskName,webenvarg)
    killCmd = "killall -9 %s" % taskName
    startCmd = "%s/%s %s%s >%s/%sPrint.log 2>&1 &" % (bin_path,taskName,webenvarg,logarg,log_path,taskName)
    psCmdOut = os.popen(psCmd).readlines()
    processCount = int(psCmdOut[0].strip())
    if processCount == 2 :
        logging.info( u"进程[%s]数量[%d],任务状态正常。" % (taskName,processCount))
    else :
        logging.info( u"进程[%s]数量[%d],进程数量不等于预期[2]，执行重启命令。" % (taskName, processCount))
        os.system(killCmd)
        sleep(1)
        os.system(startCmd)
        logging.info(u"进程[%s]启动完成。" % taskName)



if __name__ == "__main__":
    if UsualTools.isLinuxSystem():
        run_on_linux()
    else:
        run_on_linux()
