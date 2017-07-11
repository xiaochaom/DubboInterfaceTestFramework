# coding:utf-8
"""
Author:王吉亮
Date:20170117
"""

import sys,time,types,datetime,logging,time,logging.handlers

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

from Lib.DBTool import DBTool
from Lib.runWebPlatformFunc import *
from Lib.UsualTools import UsualTools
from Config.PromptMsg import PromptMsg
from DubboService.TestcaseGroup import TestcaseStep,TestcaseGroup,TestcaseDesc

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

    # =================获取所有配置======================
    confSql = "select confName,confText from tb_conf where state=1 "
    confRes = db.execute_sql(confSql)
    confDict = {}
    for res in confRes:
        tmpConfKey = res[0];
        tmpConfText = res[1]
        tmpConfPath = "%s/caseDebugenv%s.conf" % (conf_path, tmpConfKey)
        confRetCode, confConfig = getConfigObj(tmpConfKey, tmpConfText, tmpConfPath)
        confDict[tmpConfKey] = confConfig
        confDict[tmpConfKey + "code"] = confRetCode
        if confRetCode['errorCode'] != '10000':
            print u"没有得到配置文件%s，错误信息：%s" % (tmpConfKey, confRetCode['errorMsg'])
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

    webroot_path = ""
    if UsualTools.isLinuxSystem():#正式环境
        webroot_path = commonDict['web']['webroot']
    elif UsualTools.isWindowsSystem(): #王吉亮测试环境
        webroot_path = "D:/devcodes/InterfaceTestFrameworkWeb/webroot"
    elif UsualTools.isMacOS():  #liyaochao 测试环境
        webroot_path = "/Users/liyachao/PhpstormProjects/InterfaceTestFrameworkWeb/InterfaceTestFrameworkWeb/webroot"


    log_path = u"%s/logs" % base_path
    bin_path = u"%s/bin" % base_path
    print u"logPath:%s" % log_path
    print u"logLevel:%s" % logLevel
    print u"%s:%s" % (PromptMsg.loadLogPath,log_path)
    logFileName = '%s/%s.log' % (log_path, "runPlatformTaskLogging")
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

    # 循环遍历tb_task_run表，顺序执行任务，执行后填写 status 状态 1未执行 2进行中 3已执行 4执行异常
    while True:
        try:
            db = ''
            db = DBTool(sc.dbhost, sc.dbport, sc.dbusername, sc.dbpassword, sc.dbname)
            #TODO 从tb_task_run选择最近的未执行的任务 execType 立即执行、定时执行、 execLevel优先级  status 1或者2 state为1的。
            key_list = "id,taskId,`name`,`describe`,protocol,systems,caseNum,caseList,addBy,environment,execBy,execTime,execType,execLevel,`status`,isSendEmail,isCodeRate"
            sql = "select %s from tb_task_run where state=1 and (status=1 or status=2) AND execType=1 order by execLevel,addTime asc limit 1" % key_list
            # print sql
            results = db.execute_sql( sql )
            for res in results:
                try:
                    # print res
                    logging.debug(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: res in Results: " + str(res))
                    #变量赋值
                    id = res[0]
                    taskId = res[1].strip()
                    name = res[2].strip()
                    describe = res[3].strip()
                    protocol = res[4].strip()
                    systems = res[5].strip()
                    caseNum = res[6]
                    caseList = res[7].strip()
                    addBy = res[8].strip()
                    environment = res[9].strip()
                    execBy = res[10].strip()
                    execTime = res[11]
                    exectype = res[12]
                    execlevel = res[13]
                    status = res[14]
                    isSendEmail = res[15]
                    isCodeRate = res[16]

                    #开始执行任务
                    para_dict = {}
                    #获得环境
                    para_dict['env'] = environment
                    #=============生成report名字和路径等===============================================

                    para_dict['webroot'] = commonDict['web']['webroot']  #for emma 覆盖率上传
                    para_dict['uri'] = commonDict['web']['uri']   #生成回调地址等用到
                    report_base_path = "reports"
                    report_date = datetime.datetime.now().strftime('%Y%m%d')
                    report_file_date_dir = "%s/%s/%s" % (webroot_path, report_base_path, report_date)
                    report_file_name = "%s%s%s%s.html" % (protocol, execBy, environment, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
                    para_dict['report_file'] = "%s/%s" % (report_file_date_dir, report_file_name)
                    db_url = "/%s/%s/%s" % (report_base_path, report_date, report_file_name)
                    if os.path.isdir(report_file_date_dir) == False:
                        os.mkdir(report_file_date_dir)
                    #==================================================================================
                    logging.info(u"%s%s" % (PromptMsg.startTask,report_file_name))
                    logging.info(u"%s:执行任务[%s]，协议[%s],环境[%s]，执行者[%s]。" % (UsualTools.get_current_time(),name,protocol,environment, execBy))
                    # ####===========生成配置文件Start=================================================================
                    # step 1 获取配置文件
                    if protocol == "HTTP":
                        para_dict['conf'] = confDict['http']
                    else:
                        para_dict['conf'] = confDict[para_dict['env']]

                    # ####===========生成配置文件END===================================================================

                    #判断协议，进行测试
                    if protocol == "DUBBO":

                        #################################===DUBBO协议情况===#############################################################
                        #step 2 获取case_list 通过caseList分析查询。
                        para_dict['case_list'] = []
                        caseList = "'"+caseList.replace(",","','")+"'"
                        colsStr = "id,caseId,`name`,`describe`,system,service,interface,dataInit,dataRecover,parameter,expct,varsConf,addBy"
                        caseRes = db.execute_sql("select %s from tb_dubbo_case where state=1 and caseId in (%s) order by system ASC,service ASC,interface ASC,caseId ASC" % (colsStr,caseList))
                        for tmp_case in caseRes:
                            para_dict['case_list'].append({
                                'case_id': tmp_case[1],
                                'name': tmp_case[2],
                                'desc': tmp_case[3],
                                'system': tmp_case[4].replace("\n", ""),
                                'service': tmp_case[5].replace("\n", ""),
                                'method': tmp_case[6].replace("\n", ""),
                                'data_init': tmp_case[7],
                                'data_recover': tmp_case[8],
                                'params': type(tmp_case[9]) == float and str(int(tmp_case[9])) or str(tmp_case[9]).replace("\n", "").strip(),
                                'expect': type(tmp_case[10]) == float and str(int(tmp_case[10])) or str(tmp_case[10]),
                                'varsconf': str(tmp_case[11]).strip()
                            })

                        #step 3 开始执行任务，第一步判断是否要生成代码覆盖率
                        para_dict['restart'] = isCodeRate == 1 and 'YES' or 'NO'
                        para_dict['is_send_mail'] = isSendEmail == 1 and 'YES' or 'NO'
                        para_dict['mail_list'] = {}
                        #根据系统名字获取对应的email_list，中间用分号;间隔。
                        if isSendEmail == 1:
                            #初始化 emailList
                            syslist = []
                            for casevalue in para_dict['case_list']:
                                if casevalue['system'] not in syslist:
                                    syslist.append(casevalue['system'])
                            for t_sysName in syslist:
                                t_mail_res = db.execute_sql(""" select u.email  from tb_sys_user_relation su left join tb_user u on su.loginName=u.loginName
                                                             where su.state=1 and u.state=1 and su.sysName='%s' """ % (t_sysName))
                                tmpMailStr = ""
                                for tmp_email in t_mail_res:
                                    tmpMailStr = tmpMailStr+tmp_email[0]+";"
                                para_dict['mail_list'][t_sysName] = tmpMailStr
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s\n%s。" % (PromptMsg.paramMsg,para_dict))
                        sqlupdate = "update tb_task_run set status=2 where id=%s" % (id)
                        db.execute_sql(sqlupdate)
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % PromptMsg.startDubboTask)
                        ret_dict = run_platform_dubbo_task(para_dict)
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s%s。" % (PromptMsg.finishDubboTaskReturn,ret_dict))
                        ret_dict['report_file'] = db_url
                        sqlupdate = "update tb_task_run set status=3,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                    % (ret_dict['exec_result'], ret_dict['comments'].encode("utf8").replace("'",'"'), ret_dict['takeTime'],ret_dict['report_file'], id)
                        db.execute_sql(sqlupdate)
                        logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % PromptMsg.finishDubboTask)

                    elif protocol =="HTTP":

                        #################################===HTTP协议情况===#############################################################
                        # step 2 获取case_list 通过caseList分析查询。
                        para_dict['case_list'] = []
                        caseList = "'" + caseList.replace(",", "','") + "'"
                        colsStr = "id,caseId,`name`,`describe`,dataInit,dataRecover,httpRequestHead,interface,parameter,expct,varsConf,addBy"
                        caseRes = db.execute_sql(
                            "select %s from tb_http_case where state=1 and caseId in (%s) order by interface ASC,caseId ASC" % (colsStr,caseList))
                        for tmp_case in caseRes:
                            para_dict['case_list'].append({
                               'case_id': tmp_case[1].encode('utf8').replace("\n", "").strip(),
                               'name': tmp_case[2].encode('utf8'),
                               'desc': tmp_case[3].encode('utf8'),
                               'data_init': tmp_case[4].encode('utf8'),
                               'data_recover': tmp_case[5].encode('utf8'),
                               'header': tmp_case[6].encode('utf8'),
                               'url': tmp_case[7].encode('utf8').replace("\n", "").strip(),
                               'params': tmp_case[8].encode('utf8').replace("\n", "").strip(),
                               'expect': tmp_case[9].encode('utf8').strip(),
                               'varsconf': str(tmp_case[10]).encode('utf8').replace("\n", "").strip()
                            })

                        # step 3 开始执行任务，第一步判断是否要生成代码覆盖率
                        para_dict['restart'] = isCodeRate == 1 and 'YES' or 'NO' #用不到此函数
                        para_dict['is_send_mail'] = isSendEmail == 1 and 'YES' or 'NO'
                        para_dict['mail_list'] = {}
                        # 根据系统名字获取对应的email_list，中间用分号;间隔。
                        if isSendEmail == 1:
                            # 初始化 emailList
                            t_mail_res = db.execute_sql(""" select u.email  from tb_sys_user_relation su left join tb_user u on su.loginName=u.loginName
                                                                                 where su.state=1 and u.state=1 and su.sysName='%s' """ % (protocol))
                            tmpMailStr = ""
                            for tmp_email in t_mail_res:
                                tmpMailStr = tmpMailStr + tmp_email[0] + ";"
                            para_dict['mail_list'] = tmpMailStr

                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s\n%s。" % (PromptMsg.paramMsg,para_dict))
                        sqlupdate = "update tb_task_run set status=2 where id=%s" % (id)
                        db.execute_sql(sqlupdate)
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % PromptMsg.startHttpTask)
                        ret_dict = run_platform_http_task(para_dict)
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s%s。" % (PromptMsg.finishHttpTaskReturn,ret_dict))
                        ret_dict['report_file'] = db_url
                        sqlupdate = "update tb_task_run set status=3,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                    % (ret_dict['exec_result'], ret_dict['comments'].encode("utf8").replace("'",'"'), ret_dict['takeTime'],
                                       ret_dict['report_file'], id)
                        db.execute_sql(sqlupdate)
                        logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % PromptMsg.finishHttpTask)

                    else:
                        #################################===错误协议情况===#############################################################
                        tmpText = u"%s%s." % (PromptMsg.protocolError, protocol)
                        print tmpText
                        logging.info(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % tmpText)
                        sqlupdate = "update tb_task_run set status=4,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                    % (4, tmpText.replace("'", '"'), '0', '', id)
                        db.execute_sql(sqlupdate)

                except Exception,e:
                    tmpText = u"%s%s." % (PromptMsg.otherException, e.message)
                    logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % tmpText)
                    sqlupdate = "update tb_task_run set status=4,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                % (4, tmpText.replace("'",'"'), '0', '', id)
                    db.execute_sql(sqlupdate)

        except Exception,e:
            tmpText = u"%s%s." % (PromptMsg.otherException,e.message)
            print tmpText
            logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % tmpText)

        finally:
            try:
                if type(db) != type(''):
                    db.release()
            finally:
                time.sleep(0.5)
        # break #测试单次执行使用

def run_platform_test_with_group_case():
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

    # =================获取所有配置======================
    confSql = "select confName,confText from tb_conf where state=1 "
    confRes = db.execute_sql(confSql)
    confDict = {}
    for res in confRes:
        tmpConfKey = res[0];
        tmpConfText = res[1]
        tmpConfPath = "%s/caseDebugenv%s.conf" % (conf_path, tmpConfKey)
        confRetCode, confConfig = getConfigObj(tmpConfKey, tmpConfText, tmpConfPath)
        confDict[tmpConfKey] = confConfig
        confDict[tmpConfKey + "code"] = confRetCode
        if confRetCode['errorCode'] != '10000':
            print u"没有得到配置文件%s，错误信息：%s" % (tmpConfKey, confRetCode['errorMsg'])
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

    webroot_path = ""
    if UsualTools.isLinuxSystem():#正式环境
        webroot_path = commonDict['web']['webroot']
    elif UsualTools.isWindowsSystem(): #王吉亮测试环境
        webroot_path = "D:/devcodes/InterfaceTestFrameworkWeb/webroot"
    elif UsualTools.isMacOS():  #liyaochao 测试环境
        webroot_path = "/Users/liyachao/PhpstormProjects/InterfaceTestFrameworkWeb/InterfaceTestFrameworkWeb/webroot"


    log_path = u"%s/logs" % base_path
    bin_path = u"%s/bin" % base_path
    print u"logPath:%s" % log_path
    print u"logLevel:%s" % logLevel
    print u"%s:%s" % (PromptMsg.loadLogPath,log_path)
    logFileName = '%s/%s.log' % (log_path, "runPlatformTaskLogging")
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

    # 循环遍历tb_task_run表，顺序执行任务，执行后填写 status 状态 1未执行 2进行中 3已执行 4执行异常
    while True:
        try:
            db = ''
            db = DBTool(sc.dbhost, sc.dbport, sc.dbusername, sc.dbpassword, sc.dbname)
            #TODO 从tb_task_run选择最近的未执行的任务 execType 立即执行、定时执行、 execLevel优先级  status 1或者2 state为1的。
            key_list = "id,taskId,`name`,`describe`,protocol,systems,caseNum,caseList,addBy,environment,execBy,execTime,execType,execLevel,`status`,isSendEmail,isCodeRate"
            sql = "select %s from tb_task_run where state=1 and (status=1 or status=2) AND execType=1 order by execLevel,addTime asc limit 1" % key_list
            # print sql
            results = db.execute_sql( sql )
            for res in results:
                try:
                    # print res
                    logging.debug(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: res in Results: " + str(res))
                    #变量赋值
                    id = res[0]
                    taskId = res[1].strip()
                    name = res[2].strip()
                    describe = res[3].strip()
                    protocol = res[4].strip()
                    systems = res[5].strip()
                    caseNum = res[6]
                    caseList = res[7].strip()
                    addBy = res[8].strip()
                    environment = res[9].strip()
                    execBy = res[10].strip()
                    execTime = res[11]
                    exectype = res[12]
                    execlevel = res[13]
                    status = res[14]
                    isSendEmail = res[15]
                    isCodeRate = res[16]

                    #开始执行任务
                    para_dict = {}
                    #获得环境
                    para_dict['env'] = environment
                    #=============生成report名字和路径等===============================================

                    para_dict['webroot'] = commonDict['web']['webroot']  #for emma 覆盖率上传
                    para_dict['uri'] = commonDict['web']['uri']   #生成回调地址等用到
                    report_base_path = "reports"
                    report_date = datetime.datetime.now().strftime('%Y%m%d')
                    report_file_date_dir = "%s/%s/%s" % (webroot_path, report_base_path, report_date)
                    report_file_name = "%s%s%s%s.html" % (protocol, execBy, environment, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
                    para_dict['report_file'] = "%s/%s" % (report_file_date_dir, report_file_name)
                    db_url = "/%s/%s/%s" % (report_base_path, report_date, report_file_name)
                    if os.path.isdir(report_file_date_dir) == False:
                        os.mkdir(report_file_date_dir)
                    #==================================================================================
                    logging.info(u"%s%s" % (PromptMsg.startTask,report_file_name))
                    logging.info(u"%s:执行任务[%s]，协议[%s],环境[%s]，执行者[%s]。" % (UsualTools.get_current_time(),name,protocol,environment, execBy))
                    # ####===========生成配置文件Start=================================================================
                    # step 1 获取配置文件
                    if protocol == "HTTP":
                        para_dict['conf'] = confDict['http']
                    else:
                        para_dict['conf'] = confDict[para_dict['env']]

                    # ####===========生成配置文件END===================================================================

                    #判断协议，进行测试
                    if protocol == "DUBBO":

                        #################################===DUBBO协议情况===#############################################################
                        #step 2 获取case_list 通过caseList分析查询。
                        para_dict['case_list'] = []
                        caseList = "'"+caseList.replace(",","','")+"'"

                        #获取单接口用例tb_dubbo_case
                        colsStr = "id,caseId,`name`,`describe`,system,service,interface,dataInit,dataRecover,parameter,expct,varsConf,addBy"
                        caseRes = db.execute_sql("select %s from tb_dubbo_case where state=1 and caseId in (%s) order by system ASC,service ASC,interface ASC,caseId ASC" % (colsStr,caseList))
                        for tmp_case in caseRes:
                            tgcGroup = TestcaseGroup()
                            tgcGroup.tgcType = "INTERFACE"
                            # 构建TesecaseDesc
                            tgcDesc = TestcaseDesc()
                            tgcDesc.id = tmp_case[0]
                            tgcDesc.caseId = tmp_case[1]
                            tgcDesc.name = tmp_case[2]
                            tgcDesc.desc = tmp_case[3]
                            tgcDesc.stepCount = 1
                            tgcDesc.systems = tmp_case[4]
                            tgcDesc.addBy = tmp_case[12]
                            tgcGroup.tgcDesc = tgcDesc
                            # 构建stepList
                            tgcStepList = []
                            # 获取组合用例步骤根据用例id tb_dubbo_group_case_step
                            tmpStepObj = TestcaseStep()
                            tmpStepObj.id = tmp_case[0]
                            tmpStepObj.caseId = tmp_case[1]
                            tmpStepObj.step = 1
                            tmpStepObj.name = tmp_case[2]
                            tmpStepObj.desc = tmp_case[3]
                            tmpStepObj.system = tmp_case[4]
                            tmpStepObj.service = tmp_case[5]
                            tmpStepObj.method = tmp_case[6]
                            tmpStepObj.data_init = tmp_case[7]
                            tmpStepObj.data_recover = tmp_case[8]
                            tmpStepObj.params = tmp_case[9]
                            tmpStepObj.expect = tmp_case[10]
                            tmpStepObj.varsconf = tmp_case[11]
                            tmpStepObj.addBy = tmp_case[12]
                            tgcStepList.append(tmpStepObj)
                            tgcGroup.tgcStepList = tgcStepList
                            para_dict['case_list'].append(tgcGroup)

                        # 获取组合用例 tb_dubbo_group_case
                        colsStr = "id,GCId,`name`,`describe`,stepCount,systems,addBy"
                        caseRes = db.execute_sql("select %s from tb_dubbo_group_case where state=1 and GCId in (%s) order by systems ASC" % (colsStr,caseList))
                        for tmp_case in caseRes:
                            tgcGroup = TestcaseGroup()
                            tgcGroup.tgcType = "GROUP"
                            #构建TesecaseDesc
                            tgcDesc = TestcaseDesc()
                            tgcDesc.id = int(tmp_case[0])
                            tgcDesc.caseId = tmp_case[1]
                            tgcDesc.name = tmp_case[2]
                            tgcDesc.desc = tmp_case[3]
                            tgcDesc.stepCount = tmp_case[4]
                            tgcDesc.systems = tmp_case[5]
                            tgcDesc.addBy = tmp_case[6]
                            tgcGroup.tgcDesc = tgcDesc
                            #构建stepList
                            tgcStepList = []
                            # 获取组合用例步骤根据用例id tb_dubbo_group_case_step
                            colsStr = "id,GCId,stepId,`name`,`describe`,system,service,interface,dataInit,dataRecover,parameter,expect,varsConf,addBy"
                            caseStepRes = db.execute_sql(
                                "select %s from tb_dubbo_group_case_step where state=1 and GCId='%s' order by stepId ASC" % (
                                colsStr, tgcDesc.caseId))
                            for tmpCaseStep in caseStepRes:
                                tmpStepObj = TestcaseStep()
                                tmpStepObj.id = tmpCaseStep[0]
                                tmpStepObj.caseId = tmpCaseStep[1]
                                tmpStepObj.step = int(tmpCaseStep[2])
                                tmpStepObj.name = tmpCaseStep[3]
                                tmpStepObj.desc = tmpCaseStep[4]
                                tmpStepObj.system = tmpCaseStep[5]
                                tmpStepObj.service = tmpCaseStep[6]
                                tmpStepObj.method = tmpCaseStep[7]
                                tmpStepObj.data_init = tmpCaseStep[8]
                                tmpStepObj.data_recover = tmpCaseStep[9]
                                tmpStepObj.params = tmpCaseStep[10]
                                tmpStepObj.expect = tmpCaseStep[11]
                                tmpStepObj.varsconf = tmpCaseStep[12]
                                tmpStepObj.addBy = tmpCaseStep[13]
                                tgcStepList.append(tmpStepObj)
                            tgcGroup.tgcStepList = tgcStepList
                            if tgcGroup.validateSteps():
                                para_dict['case_list'].append(tgcGroup)


                        #step 3 开始执行任务，第一步判断是否要生成代码覆盖率
                        para_dict['restart'] = isCodeRate == 1 and 'YES' or 'NO'
                        para_dict['is_send_mail'] = isSendEmail == 1 and 'YES' or 'NO'
                        para_dict['mail_list'] = {}
                        #根据系统名字获取对应的email_list，中间用分号;间隔。
                        if isSendEmail == 1:
                            #初始化 emailList
                            syslist = []
                            for casevalue in para_dict['case_list']:
                                for stepvalue in casevalue.tgcStepList:
                                    if stepvalue.system not in syslist:
                                        syslist.append(stepvalue.system)
                            for t_sysName in syslist:
                                t_mail_res = db.execute_sql(""" select u.email  from tb_sys_user_relation su left join tb_user u on su.loginName=u.loginName
                                                             where su.state=1 and u.state=1 and su.sysName='%s' """ % (t_sysName))
                                tmpMailStr = ""
                                for tmp_email in t_mail_res:
                                    tmpMailStr = tmpMailStr+tmp_email[0]+";"
                                para_dict['mail_list'][t_sysName] = tmpMailStr
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s\n%s。" % (PromptMsg.paramMsg,para_dict))
                        sqlupdate = "update tb_task_run set status=2 where id=%s" % (id)
                        db.execute_sql(sqlupdate)
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % PromptMsg.startDubboTask)
                        ret_dict = run_platform_dubbo_group_case_task(para_dict)
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s%s。" % (PromptMsg.finishDubboTaskReturn,ret_dict))
                        ret_dict['report_file'] = db_url
                        sqlupdate = "update tb_task_run set status=3,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                    % (ret_dict['exec_result'], ret_dict['comments'].encode("utf8").replace("'",'"'), ret_dict['takeTime'],ret_dict['report_file'], id)
                        db.execute_sql(sqlupdate)
                        logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % PromptMsg.finishDubboTask)

                    elif protocol =="HTTP":

                        #################################===HTTP协议情况===#############################################################
                        # step 2 获取case_list 通过caseList分析查询。
                        para_dict['case_list'] = []
                        caseList = "'" + caseList.replace(",", "','") + "'"
                        colsStr = "id,caseId,`name`,`describe`,dataInit,dataRecover,httpRequestHead,interface,parameter,expct,varsConf,addBy"
                        caseRes = db.execute_sql(
                            "select %s from tb_http_case where state=1 and caseId in (%s) order by interface ASC,caseId ASC" % (colsStr,caseList))
                        for tmp_case in caseRes:
                            para_dict['case_list'].append({
                               'case_id': tmp_case[1].encode('utf8').replace("\n", "").strip(),
                               'name': tmp_case[2].encode('utf8'),
                               'desc': tmp_case[3].encode('utf8'),
                               'data_init': tmp_case[4].encode('utf8'),
                               'data_recover': tmp_case[5].encode('utf8'),
                               'header': tmp_case[6].encode('utf8'),
                               'url': tmp_case[7].encode('utf8').replace("\n", "").strip(),
                               'params': tmp_case[8].encode('utf8').replace("\n", "").strip(),
                               'expect': tmp_case[9].encode('utf8').strip(),
                               'varsconf': str(tmp_case[10]).encode('utf8').replace("\n", "").strip()
                            })

                        # step 3 开始执行任务，第一步判断是否要生成代码覆盖率
                        para_dict['restart'] = isCodeRate == 1 and 'YES' or 'NO' #用不到此函数
                        para_dict['is_send_mail'] = isSendEmail == 1 and 'YES' or 'NO'
                        para_dict['mail_list'] = {}
                        # 根据系统名字获取对应的email_list，中间用分号;间隔。
                        if isSendEmail == 1:
                            # 初始化 emailList
                            t_mail_res = db.execute_sql(""" select u.email  from tb_sys_user_relation su left join tb_user u on su.loginName=u.loginName
                                                                                 where su.state=1 and u.state=1 and su.sysName='%s' """ % (protocol))
                            tmpMailStr = ""
                            for tmp_email in t_mail_res:
                                tmpMailStr = tmpMailStr + tmp_email[0] + ";"
                            para_dict['mail_list'] = tmpMailStr

                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s\n%s。" % (PromptMsg.paramMsg,para_dict))
                        sqlupdate = "update tb_task_run set status=2 where id=%s" % (id)
                        db.execute_sql(sqlupdate)
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % PromptMsg.startHttpTask)
                        ret_dict = run_platform_http_task(para_dict)
                        logging.debug(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s%s。" % (PromptMsg.finishHttpTaskReturn,ret_dict))
                        ret_dict['report_file'] = db_url
                        sqlupdate = "update tb_task_run set status=3,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                    % (ret_dict['exec_result'], ret_dict['comments'].encode("utf8").replace("'",'"'), ret_dict['takeTime'],
                                       ret_dict['report_file'], id)
                        db.execute_sql(sqlupdate)
                        logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % PromptMsg.finishHttpTask)

                    else:
                        #################################===错误协议情况===#############################################################
                        tmpText = u"%s%s." % (PromptMsg.protocolError, protocol)
                        print tmpText
                        logging.info(
                            UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % tmpText)
                        sqlupdate = "update tb_task_run set status=4,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                    % (4, tmpText.replace("'", '"'), '0', '', id)
                        db.execute_sql(sqlupdate)

                except Exception,e:
                    logging.debug(traceback.format_exc())
                    tmpText = u"%s%s." % (PromptMsg.otherException, e.message)
                    logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % tmpText)
                    sqlupdate = "update tb_task_run set status=4,execResult=%d,comments='%s',takeTime='%s',testReportUrl='%s' where id=%s" \
                                % (4, tmpText.replace("'",'"'), '0', '', id)
                    db.execute_sql(sqlupdate)

        except Exception,e:
            tmpText = u"%s%s." % (PromptMsg.otherException,e.message)
            print tmpText
            logging.info(UsualTools().get_current_time() + u"=>runPlatformTask.py: run_on_linux: %s" % tmpText)

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
        # run_on_linux()
        run_platform_test_with_group_case()
