# coding:utf-8
"""
Author:王吉亮
Date:20170117
"""

import sys,time,types,logging.handlers,threading,inspect,ctypes,traceback

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

from Lib.DBTool import DBTool
from Config.GlobalConf import ServiceConf
from Lib.runWebPlatformFunc import *
from Lib.UsualTools import UsualTools
from Config.PromptMsg import PromptMsg

from DubboService.TestcaseHttpGroup import TestcaseHttpGroup
from DubboService.TestcaseHttpDesc import TestcaseHttpDesc
from DubboService.TestcaseHttpStep import TestcaseHttpStep
from DubboService.CommonProcess import CommonProcess

from Config.Const import *
#停止线程
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
#停止线程
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

def thread_run_dubbo_debug(res,confDict,db):
    try:
        para_dict = {}
        para_dict['case_list'] = [{}]
        para_dict['case_list'][0]['case_id'] = "TC_%s_1" % res[4].strip()
        para_dict['case_list'][0]['name'] = res[2].replace("\r\n", '')
        para_dict['case_list'][0]['desc'] = res[3].strip()
        para_dict['case_list'][0]['system'] = res[4].replace("\r\n", '')
        para_dict['case_list'][0]['service'] = res[5].replace("\r\n", '')
        para_dict['case_list'][0]['method'] = res[6].replace("\r\n", '')
        para_dict['case_list'][0]['data_init'] = res[7].strip()
        para_dict['case_list'][0]['data_recover'] = res[8].strip()
        para_dict['case_list'][0]['params'] = res[9].replace("\r\n", '')
        para_dict['case_list'][0]['expect'] = res[10].strip()
        para_dict['case_list'][0]['varsconf'] = res[11].strip()
        para_dict['env'] = res[12].strip()

        print u"%s:当前调试环境[%s]，调试人员[%s]，协议[DUBBO]。" % (UsualTools.get_current_time(), para_dict['env'], res[13])
        logging.info(u"当前调试环境[%s]，调试人员[%s]，协议[DUBBO]。" % (para_dict['env'], res[13]))
        confKey = para_dict['env'].strip()
        para_dict['conf'] = confDict[confKey]

        # 构建用例
        logging.info(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % PromptMsg.startDebugTask)
        case_list_with_testresult, take_time = debug_case(para_dict)
        logging.debug(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: case_list_with_testresult::%s" % case_list_with_testresult)
        logging.debug(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: =>takeTime：%s" % str(
                take_time))
        if case_list_with_testresult[0]['test_result'] in [PASS, FAIL, ERROR]:
            logging.info(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % PromptMsg.execSuccess)
            sqlupdate = """update tb_dubbo_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s',initTakeTime='%s',execTakeTime='%s',recoverTakeTime='%s',
                      dataInit='%s',dataRecover='%s',parameter='%s',expct='%s' where id=%s""" \
                        % (case_list_with_testresult[0]['return_msg'].replace("'", '"'),
                           case_list_with_testresult[0]['assert_msg'].replace("'", '"'),
                           str(case_list_with_testresult[0]['initTakeTime'] + case_list_with_testresult[0][
                               'execTakeTime'] + case_list_with_testresult[0]['recoverTakeTime']),
                           str(case_list_with_testresult[0]['initTakeTime']),
                           str(case_list_with_testresult[0]['execTakeTime']),
                           str(case_list_with_testresult[0]['recoverTakeTime']),
                           case_list_with_testresult[0]['data_init'].replace("'", '"'),
                           case_list_with_testresult[0]['data_recover'].replace("'", '"'),
                           case_list_with_testresult[0]['params'].replace("'", '"'),
                           case_list_with_testresult[0]['expect'].replace("'", '"'),
                           res[0])
            logging.debug(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % sqlupdate)
            db.execute_sql(sqlupdate)
            logging.info(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % PromptMsg.intoDbSuccess)
            logging.info(
                "=====================================================================================================")
        else:
            logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED failed!")
            tmpText = PromptMsg.debugFailMsg
            logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % tmpText)
            sqlupdate = "update tb_dubbo_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s' where id=%s" \
                        % (tmpText, tmpText, '0', res[0])
            logging.debug(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % sqlupdate)
            db.execute_sql(sqlupdate)
            logging.info(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED failed INTODB successfully!")
            logging.info(
                "=====================================================================================================")

    except Exception, e:
        logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % e)
        logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED exception!")
        tmpText = u"%s:%s" % (PromptMsg.exceptionAndCheck, e)
        logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % tmpText)
        sqlupdate = "update tb_dubbo_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s' where id=%s" \
                    % (tmpText, tmpText, '0', res[0])
        logging.debug(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % sqlupdate)
        db.execute_sql(sqlupdate)
        logging.info(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % PromptMsg.intoDbSuccess)
        logging.info(
            "=====================================================================================================")

def thread_run_http_debug(res,confDict,db):
    try:
        para_dict = {}
        para_dict['case_list'] = [{}]
        para_dict['case_list'][0]['case_id'] = "TC_HTTP_1"
        para_dict['case_list'][0]['name'] = res[2].replace("\r\n", '')
        para_dict['case_list'][0]['desc'] = res[3]
        para_dict['case_list'][0]['data_init'] = res[4]
        para_dict['case_list'][0]['data_recover'] = res[5]
        para_dict['case_list'][0]['header'] = res[6]
        para_dict['case_list'][0]['url'] = res[7].replace("\r\n", '')
        para_dict['case_list'][0]['params'] = res[8].replace("\r\n", '')
        para_dict['case_list'][0]['expect'] = res[9]
        para_dict['case_list'][0]['varsconf'] = res[10]
        para_dict['env'] = res[11]
        # print para_dict
        print u"%s:当前调试环境[%s]，调试人员[%s]，协议[HTTP]。" % (UsualTools.get_current_time(), para_dict['env'], res[12])
        logging.info(u"当前调试环境[%s]，调试人员[%s]，协议[HTTP]。" % (para_dict['env'], res[12]))
        para_dict['conf'] = confDict['http']

        # print para_dict
        # 构建用例
        logging.info(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % PromptMsg.startHttpDebugTask)
        case_list_with_testresult, take_time = debug_http_case(para_dict)
        logging.debug(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: case_list_with_testresult::%s" % case_list_with_testresult)
        logging.debug(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: =>takeTime：%s" % str(
                take_time))
        if case_list_with_testresult[0]['test_result'] in [PASS, FAIL, ERROR]:
            logging.info(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % PromptMsg.execSuccess)
            sqlupdate = """update tb_http_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s',initTakeTime='%s',execTakeTime='%s',recoverTakeTime='%s',parameter='%s',
                         dataInit='%s',dataRecover='%s',httpRequestHead='%s',expct='%s' where id=%s""" \
                        % (case_list_with_testresult[0]['return_msg'].replace("'", '"'),
                           case_list_with_testresult[0]['assert_msg'].replace("'", '"'),
                           str(case_list_with_testresult[0]['initTakeTime'] + case_list_with_testresult[0][
                               'execTakeTime'] + case_list_with_testresult[0]['recoverTakeTime']),
                           str(case_list_with_testresult[0]['initTakeTime']),
                           str(case_list_with_testresult[0]['execTakeTime']),
                           str(case_list_with_testresult[0]['recoverTakeTime']),
                           case_list_with_testresult[0]['params'].replace("'", '"'),
                           case_list_with_testresult[0]['data_init'].replace("'", '"'),
                           case_list_with_testresult[0]['data_recover'].replace("'", '"'),
                           case_list_with_testresult[0]['header'].replace("'", '"'),
                           case_list_with_testresult[0]['expect'].replace("'", '"'),
                           res[0])
            logging.debug(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % sqlupdate)
            db.execute_sql(sqlupdate)
            logging.info(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % PromptMsg.intoDbSuccess)
            logging.info(
                "=====================================================================================================")
        else:
            logging.info(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED failed!")
            tmpText = PromptMsg.debugFailMsg
            logging.info(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % tmpText)
            sqlupdate = "update tb_http_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s' where id=%s" \
                        % (tmpText, tmpText, '0', res[0])
            logging.debug(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % sqlupdate)
            db.execute_sql(sqlupdate)
            logging.info(
                UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED failed INTODB successfully!")
            logging.info(
                "=====================================================================================================")

    except Exception, e:
        logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % e)
        logging.info(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED exception!")
        tmpText = u"%s:%s" % (PromptMsg.exceptionAndCheck, e)
        logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % tmpText)
        sqlupdate = "update tb_http_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s' where id=%s" \
                    % (tmpText, tmpText, '0', res[0])
        logging.debug(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % sqlupdate)
        db.execute_sql(sqlupdate)
        logging.info(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % PromptMsg.intoDbSuccess)
        logging.info(
            "=====================================================================================================")

        ###########################处理tb_http_debug   END ######################################################

        ###########################处理tb_http_debug#END#######################################################

def thread_run_http_group_debug(group_case_list,confDict,env,db):
    try:
        tmpId = group_case_list[0].tgcStepList[0].id
        tmpGCId = group_case_list[0].tgcStepList[0].caseId

        para_dict = {}
        para_dict['case_list'] = group_case_list
        para_dict['env'] = env
        addBy = group_case_list[0].tgcDesc.addBy

        # print para_dict
        print u"%s:当前调试环境[%s]，调试人员[%s]，协议[HTTP]。" % (UsualTools.get_current_time(), para_dict['env'], addBy)
        logging.info(u"当前调试环境[%s]，调试人员[%s]，协议[HTTP]。" % (para_dict['env'], addBy))
        para_dict['conf'] = confDict['http']

        # print para_dict
        # 构建用例
        logging.info(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % PromptMsg.startHttpDebugTask)
        case_list_with_testresult, take_time = debug_http_group_case(para_dict)
        logging.debug(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: case_list_with_testresult::%s" % case_list_with_testresult)
        logging.debug(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: =>takeTime：%s" % str(
                take_time))

        tgc = case_list_with_testresult[0]
        tgcDesc = tgc.tgcDesc
        tgcStepList = tgc.tgcStepList
        for tmpTgcStep in tgcStepList:
            tmpId = tmpTgcStep.id
            if tmpTgcStep.test_result in [PASS, FAIL, ERROR]:
                headIntoDb = """URI:[%s];
METHOD:[%s];
HEADER:[%s];""" % (tmpTgcStep.host,tmpTgcStep.method,tmpTgcStep.header)
                logging.info(
                    UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % PromptMsg.execSuccess)
                sqlupdate = """update tb_http_group_case_step_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s',initTakeTime='%s',execTakeTime='%s',recoverTakeTime='%s',parameter='%s',
                             dataInit='%s',dataRecover='%s',httpRequestHead='%s',expect='%s' where id=%s""" \
                            % (tmpTgcStep.return_msg.replace("'", '"'),
                               tmpTgcStep.assert_msg.replace("'", '"'),
                               str(tmpTgcStep.totalTakeTime),
                               str(tmpTgcStep.initTakeTime),
                               str(tmpTgcStep.execTakeTime),
                               str(tmpTgcStep.recoverTakeTime),
                               tmpTgcStep.params.replace("'", '"'),
                               tmpTgcStep.data_init.replace("'", '"'),
                               tmpTgcStep.data_recover.replace("'", '"'),
                               headIntoDb.replace("'", '"'),
                               tmpTgcStep.expect.replace("'", '"'),
                               tmpId)
                logging.debug(
                    UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % sqlupdate)
                db.execute_sql(sqlupdate)
                logging.info(
                    UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % PromptMsg.intoDbSuccess)
                logging.info(
                    "=====================================================================================================")
            else:
                logging.info(
                    UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED failed!")
                tmpText = PromptMsg.debugFailMsg
                logging.info(
                    UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % tmpText)
                sqlupdate = "update tb_http_group_case_step_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s' where id=%s" \
                            % (tmpText, tmpText, '0', tmpId)
                logging.debug(
                    UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % sqlupdate)
                db.execute_sql(sqlupdate)
                logging.info(
                    UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED failed INTODB successfully!")
                logging.info(
                    "=====================================================================================================")

        sqlupdate = """update tb_http_group_case_step_debug set status=2 where addBy="%s" """  % addBy
        logging.debug(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % sqlupdate)
        db.execute_sql(sqlupdate)
    except Exception, e:
        logging.debug(traceback.format_exc())
        logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % e)
        logging.info(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: EXECUTED exception!")
        tmpText = u"%s:%s" % (PromptMsg.exceptionAndCheck, e)
        logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % tmpText)
        sqlupdate = "update tb_http_group_case_step_debug set status=2,returnMsg='%s',assertMsg='%s',takeTime='%s' where id=%s" \
                    % (tmpText, tmpText, '0', tmpId)
        logging.debug(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % sqlupdate)
        db.execute_sql(sqlupdate)
        logging.info(
            UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s" % PromptMsg.intoDbSuccess)
        logging.info(
            "=====================================================================================================")

        ###########################tb_http_group_case_step_debug   END ######################################################

def run_on_linux():
    # --log=INFO--webenv=test
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
        print u"windows 只能运行测试环境！"
        logLevel = 'DEBUG'
        testenv = 'test'
    elif UsualTools.isMacOS():
        print u"macOS 只能运行测试环境！"
        logLevel = 'DEBUG'
        testenv = 'test'

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

    #=================获取所有配置======================
    confSql = "select confName,confText from tb_conf where state=1 "
    confRes = db.execute_sql(confSql)
    confDict = {}
    for res in confRes:
        tmpConfKey = res[0];
        tmpConfText = res[1]
        tmpConfPath = "%s/caseDebugenv%s.conf" % (conf_path,tmpConfKey)
        confRetCode,confConfig = getConfigObj(tmpConfKey,tmpConfText,tmpConfPath)
        confDict[tmpConfKey] = confConfig
        confDict[tmpConfKey+"code"] = confRetCode
        if confRetCode['errorCode'] != '10000':
            print u"没有得到配置文件%s，错误信息：%s" % (tmpConfKey,confRetCode['errorMsg'])
            db.release()
            sys.exit(0);

    db.release()
    ##################################################################################################

    # IMP:不能用../定位的原因是在平台上要用绝对路径执行程序，用../定位不到配置文件，只能用绝对路径
    commonDict = confDict['commonconf'].conf_dict
    base_path=""
    if UsualTools.isLinuxSystem(): #正式环境
        base_path = commonDict['platform']['basepath']
    elif UsualTools.isWindowsSystem(): #王吉亮测试环境
        base_path = "D:/devcodes/DubboInterfaceTestFramework/DubboInterfaceTestFramework"
    elif UsualTools.isMacOS(): #liyaochao 测试环境
        base_path = "/Users/liyachao/PycharmProjects/DubboInterfaceTestFramework"

    log_path = u"%s/logs" % base_path
    bin_path = u"%s/bin" % base_path
    print u"logPath:%s" % log_path
    print u"logLevel:%s" % logLevel
    print u"%s:%s" % (PromptMsg.loadLogPath,log_path)
    logFileName = '%s/%s.log' % (log_path, "caseDebugTaskLogging")
    print u"logFileName:%s" % logFileName

    #################################################################################################
    # 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logLevel=="INFO" and logging.INFO or logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(logFileName, maxBytes=1024 * 1024 * 10, backupCount=5)  # 实例化handler
    logger.addHandler(handler)
    #################################################################################################
    logging.info(UsualTools().get_current_time() + (u"=>runPlatformTask.py: run_on_linux: logPath: %s " % log_path))
    logging.info(UsualTools().get_current_time() + (u"=>runPlatformTask.py: run_on_linux: logLevel: %s " % logLevel))

    # 循环遍历tb_dubbo_debug  tb_http_debug表，顺序执行任务，执行后填写 status 状态 1未执行 2已执行
    thread_dict = {}  # 存放调试线程，key是调试人员，value是线程。
    while True:
        try:
            db = DBTool(sc.dbhost, sc.dbport, sc.dbusername, sc.dbpassword, sc.dbname)
            ##########################处理tb_dubbo_debug#########################################################
            colsStr = "id,caseId,`name`,`describe`,system,service,interface,dataInit,dataRecover,parameter,expct,varsConf,environment,addBy"
            resultsDubbo = db.execute_sql("select %s from tb_dubbo_debug where state=1 and status=1 order by addTime asc" % colsStr)
            for res in resultsDubbo:
                debugUser = res[13]
                #增加线程退出
                try:
                    if "threading.Thread" in str(type(thread_dict[debugUser])):
                        #有存在的线程，退出。
                        stop_thread(thread_dict[debugUser])
                except Exception,e:
                    logging.debug(u"用户[%s]没有启动任何线程。异常：%s" % (debugUser,e))
                finally:
                    #没有线程或者没有这个key的记录,启动线程加入到dict中。
                    tmpDubboThread = threading.Thread(target=thread_run_dubbo_debug, args=(res,confDict,db))
                    tmpDubboThread.start()
                    thread_dict[debugUser] = tmpDubboThread
                    logging.debug(u"当前用户[%s]线程id[%s]" % (debugUser,thread_dict[debugUser]))

            ##########################处理tb_dubbo_debug      END#################################################
            ###########################处理tb_http_debug##########################################################
            colsStr = "id,caseId,`name`,`describe`,dataInit,dataRecover,httpRequestHead,interface,parameter,expct,varsConf,environment,addBy"
            resultsHttp = db.execute_sql("select %s from tb_http_debug where state=1 and status=1 order by addTime asc" % colsStr)
            # print "select %s from tb_http_debug where state=1 and status=1 order by addTime asc" % colsStr
            for res in resultsHttp:
                debugUser = res[12]
                # 增加线程退出
                try:
                    if "threading.Thread" in str(type(thread_dict[debugUser])):
                        # 有存在的线程，退出。
                        stop_thread(thread_dict[debugUser])
                except Exception, e:
                    logging.debug(u"用户[%s]没有启动任何线程。异常：%s" % (debugUser, e))
                finally:
                    # 没有线程或者没有这个key的记录,启动线程加入到dict中。
                    tmpDubboThread = threading.Thread(target=thread_run_http_debug, args=(res, confDict, db))
                    tmpDubboThread.start()
                    thread_dict[debugUser] = tmpDubboThread
                    logging.debug(u"当前用户[%s]线程id[%s]" % (debugUser, thread_dict[debugUser]))

            ###########################处理tb_http_debug#######END################################################
            ###########################处理tb_http_group_debug##########################################################
            sqlGetGCIds = "select distinct(GCId) from tb_http_group_case_step_debug where state=1 and status=1 order by addTime asc"
            resGCId = db.execute_sql(sqlGetGCIds)
            for tmpGCId in resGCId:
                gcId = tmpGCId[0]
                colsStr = "id,GCId,stepId,`name`,`describe`,dataInit,dataRecover,httpRequestHead,interface,parameter,expect,varsConf,resultVal,environment,addBy"
                resultsHttpGroup = db.execute_sql("select %s from tb_http_group_case_step_debug where GCId = '%s' order by stepId asc" % (colsStr,gcId))
                # print "select %s from tb_http_debug where state=1 and status=1 order by addTime asc" % colsStr
                debugUser = ''
                env = ''
                tgc = TestcaseHttpGroup()
                tgcDesc = TestcaseHttpDesc()
                tgcDesc.caseId = gcId
                tgc.tgcType = "GROUP"
                tgc.tgcDesc = tgcDesc
                tgcStepList = []
                for tmpStpeRes in resultsHttpGroup:
                    if env == '':
                        env = tmpStpeRes[13]
                    if debugUser == '':
                        debugUser = tmpStpeRes[14]
                    tmpTgcStep = TestcaseHttpStep()
                    tmpTgcStep.id = tmpStpeRes[0]
                    tmpTgcStep.caseId = tmpStpeRes[1]
                    tmpTgcStep.stepId = tmpStpeRes[2]
                    tmpTgcStep.name = tmpStpeRes[3]
                    tmpTgcStep.desc = tmpStpeRes[4]
                    tmpTgcStep.data_init = tmpStpeRes[5]
                    tmpTgcStep.data_recover = tmpStpeRes[6]

                    cp = CommonProcess()
                    httpRequestHead = tmpStpeRes[7]  #通过Head解析出来uri，method，header
                    tmpTgcStep.host = cp.get_sub_string(httpRequestHead, "URI:[", "];")  # "http://www.baidu.com:9999等"
                    tmpTgcStep.method = cp.get_sub_string(httpRequestHead, "METHOD:[", "];").strip().lower()  # POST or GET
                    tmpTgcStep.header = cp.get_sub_string(httpRequestHead, "HEADER:[", "];")  # 键值对应的header

                    tmpTgcStep.url = tmpStpeRes[8]
                    tmpTgcStep.params = tmpStpeRes[9]
                    tmpTgcStep.expect = tmpStpeRes[10]
                    tmpTgcStep.varsconf = tmpStpeRes[11]
                    tmpTgcStep.varsconf_result = tmpStpeRes[12]
                    tmpTgcStep.addBy = tmpStpeRes[14]
                    tgcStepList.append(tmpTgcStep)


                tgc.tgcStepList = tgcStepList
                tgc.tgcDesc.addBy = debugUser
                tgc.sortSteps()
                tgc.validateSteps()

                group_case_list = [tgc]
                # 增加线程退出
                try:
                    if "threading.Thread" in str(type(thread_dict[debugUser])):
                        # 有存在的线程，退出。
                        stop_thread(thread_dict[debugUser])
                except Exception, e:
                    logging.debug(traceback.format_exc())
                    logging.debug(u"用户[%s]没有启动任何线程。异常：%s" % (debugUser, e))
                finally:
                    # 没有线程或者没有这个key的记录,启动线程加入到dict中。
                    tmpDubboThread = threading.Thread(target=thread_run_http_group_debug, args=(group_case_list, confDict,env, db))
                    tmpDubboThread.start()
                    thread_dict[debugUser] = tmpDubboThread
                    logging.debug(u"当前用户[%s]线程id[%s]" % (debugUser, thread_dict[debugUser]))
            ###########################处理tb_http_group_debug#######END################################################

        except Exception,e:
            logging.debug(traceback.format_exc())
            tmpText = u"%s%s" % (PromptMsg.otherException,e)
            logging.info(UsualTools().get_current_time() + u"=>runCaseDebugTask.py: run_on_linux: %s " % tmpText)

        finally:
            try:
                db.release()
            finally:
                time.sleep(0.5)

if __name__ == "__main__":
    if UsualTools.isLinuxSystem():
        run_on_linux()
    else:
        run_on_linux()
