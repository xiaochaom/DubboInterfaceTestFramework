# coding:utf-8
"""
Author:王吉亮
Date:20170214
comments: 用例执行时取消的功能
"""

import sys,time,types,datetime,logging.handlers

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

from Lib.DBTool import DBTool
from Lib.runWebPlatformFunc import *
from Lib.UsualTools import UsualTools
from Config.PromptMsg import PromptMsg

def run_on_linux():
    import time
    logging.basicConfig(level= logging.DEBUG)  #初始化logging
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
    #初始化数据库配置conf
    sc = ServiceConf(testenv)
    db = DBTool(sc.dbhost, sc.dbport, sc.dbusername, sc.dbpassword, sc.dbname)

    conf_path = ""
    if UsualTools.isLinuxSystem():#正式环境
        conf_path = "/home"
    elif UsualTools.isWindowsSystem(): #王吉亮测试环境
        conf_path = "D:/devcodes/DubboInterfaceTestFramework/DubboInterfaceTestFramework"
    elif UsualTools.isMacOS(): #liyaochao测试环境
        conf_path = "/home"
        
    commonRetCode, commnonConfig = getConfFromDB(db, "commonconf", confPath=conf_path+"/taskCancelcommonconf.conf")
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
    print u"%s:%s" % (PromptMsg.loadLogPath,log_path)
    logFileName = '%s/%s.log' % (log_path, "taskCancelLogging")
    print u"logFileName:%s" % logFileName

    #################################################################################################
    # 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logLevel=="INFO" and logging.INFO or logging.DEBUG)
    # handler = logging.FileHandler(logFileName)
    handler = logging.handlers.RotatingFileHandler(logFileName, maxBytes=1024 * 1024 * 10, backupCount=5)  # 实例化handler
    logger.addHandler(handler)

    #################################################################################################

    logging.info(UsualTools().get_current_time() + (u"=>runPlatformTask.py: run_on_linux: logPath: %s " % log_path))
    logging.info(UsualTools().get_current_time() + (u"=>runPlatformTask.py: run_on_linux: logLevel: %s " % logLevel))


    # 循环遍历tb_task_run表，顺序执行任务，执行后填写 status 状态 1未执行 2进行中 3已执行 4执行异常
    while True:
        try:
            db = ''
            db = DBTool(sc.dbhost, sc.dbport, sc.dbusername, sc.dbpassword, sc.dbname)
            key_list = "id,taskId,`name`,`describe`,protocol,systems,caseNum,caseList,addBy,environment,execBy,execTime,execType,execLevel,`status`,isSendEmail,isCodeRate"
            results = db.execute_sql("select %s from tb_task_run where state=1 and (status=1 or status=2 or status=10) AND execType=1 order by addTime asc limit 1" % key_list )
            # (status=1 or status=2 or status=10) 这个判定是保证当前执行的不是取消状态，如果当前是取消状态再去取消，否则继续执行。
            for res in results:
                #变量赋值
                id = res[0]
                taskId = res[1]
                status = res[14]  # 1待执行 2执行中 3执行完成 4执行异常 10待取消 11已取消
                if status == 10:
                    stopPlatformTask = "killall -9 runPlatformTask"
                    startPlatformTask = "%s/runPlatformTask --webenv=%s--log=%s >%s/runPlatformTaskPrint.log  2>&1 &" % (bin_path,testenv, logLevel, log_path)
                    os.system(stopPlatformTask)
                    tmpText = u"%s%s" % (PromptMsg.taskCanceled,taskId)
                    print tmpText
                    logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % tmpText)
                    sqlupdate = "update tb_task_run set status=11,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                % (11, u"任务已取消。", '0', '', id)
                    db.execute_sql(sqlupdate)
                    #重启runPlatformTask.py ，此时将跳过已经取消的任务执行下一个
                    os.system(stopPlatformTask)
                    os.system(startPlatformTask)
                    continue

                sleep(1)

        except Exception,e:
            tmpText = u"%s%s." % (PromptMsg.otherException,e)
            print tmpText
            logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % tmpText)
            sqlupdate = "update tb_task_run set status=4,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                        % (4, tmpText.replace("'",'"'), '0', '', id)
            db.execute_sql(sqlupdate)
        finally:
            try:
                if type(db) != type(''):
                    db.release()
            finally:
                time.sleep(0.5)
        # break #测试单次执行使用

if __name__ == "__main__":
    if UsualTools.isLinuxSystem():
        run_on_linux()
    else:
        run_on_linux()
