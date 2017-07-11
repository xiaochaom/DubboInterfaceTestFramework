# coding:utf-8
"""
Author:王吉亮
Date:20170117
"""

import sys, os, logging,paramiko,types

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

import traceback
from Lib.runfunc import *
from Config.PromptMsg import PromptMsg
from DubboService.TestcaseGroup import TestcaseDesc,TestcaseGroup,TestcaseStep
#==========================DUBBO=====START=====================================

def getArgsDict(argStr):
    argList = argStr.split("--")
    argDict = {}
    for arg in argList:
        if arg.strip()!="":
            tArgList = arg.split("=")
            if len(tArgList) == 2:
                argDict[tArgList[0]] = tArgList[1]
            else:
                print "Argument[%s] error! " % arg
    return argDict

def debug_case(para_dict):
    """执行单个测试用例，并返回测试结果。
    """
    case_list = para_dict['case_list'] #从tb_dubbo_debug表中查出数据。
    conf = para_dict['conf'] #根据测试环境，然后从conf表中获取，并生成对应的conf文件
    env = para_dict['env']
    time_before_execute_testcases = time()
    case_list_with_testresult = DubboService().execute_testcases(case_list, conf, env)
    time_after_execute_testcases = time()
    take_time = time_after_execute_testcases - time_before_execute_testcases
    logging.info(UsualTools().get_current_time() + u"=>runWebPlagformFunc.py: debug_case: DubboService().execute_testcases%s:%s" % (PromptMsg.funcTakeTime,str(take_time)))
    return case_list_with_testresult,take_time

def debug_http_case(para_dict):
    """执行单个测试用例，并返回测试结果。
    """

    case_list = para_dict['case_list'] #从tb_dubbo_debug表中查出数据。
    conf = para_dict['conf'] #根据测试环境，然后从conf表中获取，并生成对应的conf文件
    env = para_dict['env']
    time_before_execute_testcases = time()
    case_list_with_testresult = HttpService().execute_testcases(case_list, conf, env)
    time_after_execute_testcases = time()
    take_time = time_after_execute_testcases - time_before_execute_testcases
    logging.info(UsualTools().get_current_time() + u"=>runWebPlagformFunc.py: debug_http_case: HttpService().execute_testcases%s:%s" % (PromptMsg.funcTakeTime,str(take_time)))
    return case_list_with_testresult,take_time

def debug_http_group_case(para_dict):
    """执行单个测试用例，并返回测试结果。
    """

    case_list = para_dict['case_list'] #从tb_dubbo_debug表中查出数据。
    conf = para_dict['conf'] #根据测试环境，然后从conf表中获取，并生成对应的conf文件
    env = para_dict['env']
    time_before_execute_testcases = time()
    case_list_with_testresult = HttpService().execute_group_testcases(case_list, conf, env)
    time_after_execute_testcases = time()
    take_time = time_after_execute_testcases - time_before_execute_testcases
    logging.info(UsualTools().get_current_time() + u"=>runWebPlagformFunc.py: debug_http_case: HttpService().execute_testcases%s:%s" % (PromptMsg.funcTakeTime,str(take_time)))
    return case_list_with_testresult,take_time

def run_platform_dubbo_task(para_dict={}):
    """执行测试用例，并生成测试报告。
    """
    ret_dict = {}
    ret_dict['takeTime'] = '0'
    ret_dict['comments'] = u''
    ret_dict['exec_result'] = 4 # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
    ret_dict['report_file'] = para_dict['report_file']

    case_list = para_dict['case_list']
    conf = para_dict['conf']
    env = para_dict['env']
    result_dicts = {}
    if len(case_list) == 0:
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: 用例列表为空，执行失败！")
        ret_dict['comments'] = PromptMsg.noneCaseFail
        return ret_dict
    logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: case_list长度:%s" % len(case_list))
    time_before_execute_testcases = time()
    # 根据case_list生成系统list
    syslist = []
    for casevalue in case_list:
        if casevalue['system'] not in syslist:
            syslist.append(casevalue['system'])
    if para_dict['restart'] == "YES":
        # resetEmma and instrEmma
        bool_ret, msg = instr_and_reset_emma(syslist, conf)

    time_start = time()
    case_list_with_testresult = DubboService().execute_testcases(case_list, conf, env)
    time_end = time()
    ret_dict['takeTime'] = str(time_end-time_start)


    # generate emmaReport and scp to testwebserver，并返回系统对应的web地址的覆盖率网页。
    # 初始化urldict
    url_dict = {}
    # init ret_url_dict
    for syskey in syslist:
        url_dict[syskey] = {}
        url_dict[syskey]['url'] = "None"

    if para_dict['restart'] == "YES":
        url_dict = ctl_and_report_emma(syslist, conf,para_dict['webroot'],para_dict['uri'])

    # TODO 不同系统下根据url获取网页数据并使用beautifulSoap解析出来覆盖率信息。（也可在生成报告时获取）
    #生成报告的路径下
    try:
        logging.debug("EEEEE:%s" % url_dict)
        result_dicts = HTML_Report().generate_report(case_list_with_testresult, url_dict, para_dict['report_file'])
    except Exception, e:
        logging.debug(traceback.format_exc())
        ret_dict['comments'] = u"%s%s" % (PromptMsg.reportFailAndReason,e)
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: %s" % ret_dict['comments'])
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: %s" % PromptMsg.emailNotSend)
        return ret_dict

    isError = False
    isFail = False
    isException = False
    for k, v in result_dicts.items():
        if type(v) != type({}): continue
        logging.debug(u"系统[%s]中，总共测试用例数量[%s]，通过[%s]，失败[%s]，错误[%s]。" % (k, v['count'], v['pass'], v['fail'], v['error']))
        if v['error'] > 0 :
            isError = True
            ret_dict['comments'] = ret_dict['comments'] +u'系统[%s]测试用例存在错误，总共测试用例数量[%s]，通过[%s]，失败[%s]，错误[%s]。\n' % (k,v['count'], v['pass'], v['fail'], v['error'])
            # ret_dict['exec_result'] = 3  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
        elif v['fail'] > 0:
            isFail = True
            ret_dict['comments'] = ret_dict['comments'] +u'系统[%s]测试未通过，总共测试用例数量[%s]，通过[%s]，失败[%s]。\n' % (k,v['count'],v['pass'],v['fail'])
            # ret_dict['exec_result'] = 2  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
            if para_dict['is_send_mail'] == "YES":
                email_list = para_dict['mail_list'][k]
                title = u"Dubbo接口测试--系统%s出现失败用例%d个" % (k, result_dicts[k]['fail'])
                content = u"详情见附件测试报告。"
                for i in range(0, 10):
                    try:
                        UsualTools.send_mail(email_list, title, content, para_dict['report_file'])
                        # is_send_mail_send = True
                        break
                    except Exception, e:
                        print u"Email发送失败，尝试再次发送。原因：%s" % e
        elif v['count'] == v['pass']:
            ret_dict['comments'] = ret_dict['comments'] +u'系统[%s]测试通过，总共测试用例数量[%s]，通过[%s]。\n' % (k,v['count'],v['pass'])
            # ret_dict['exec_result'] = 1  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
        else:
            isException = True
            ret_dict['comments'] = ret_dict['comments'] +u'系统[%s]测试出现异常，总共测试用例数量[%s]，通过[%s]，失败[%s]，错误[%s]。\n' % (k,v['count'], v['pass'], v['fail'], v['error'])
            # ret_dict['exec_result'] = 4  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION

    if isException:
        ret_dict['exec_result'] = 4
    elif isError:
        ret_dict['exec_result'] = 3
    elif isFail:
        ret_dict['exec_result'] = 2
    else:
        ret_dict['exec_result'] = 1


    logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: 任务执行完毕。")
    logging.info(u"***************************************************************************************************")
    logging.info(u"***************************************************************************************************")
    return ret_dict

def run_platform_dubbo_group_case_task(para_dict={}):
    """执行测试用例，并生成测试报告。
    """
    ret_dict = {}
    ret_dict['takeTime'] = '0'
    ret_dict['comments'] = u''
    ret_dict['exec_result'] = 4 # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
    ret_dict['report_file'] = para_dict['report_file']

    case_list = para_dict['case_list']
    conf = para_dict['conf']
    env = para_dict['env']
    result_dicts = {}
    if len(case_list) == 0:
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: 用例列表为空，执行失败！")
        ret_dict['comments'] = PromptMsg.noneCaseFail
        return ret_dict
    logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: case_list长度:%s" % len(case_list))
    time_before_execute_testcases = time()
    # 根据case_list生成系统list
    syslist = []
    for casevalue in case_list:
        for stepvalue in casevalue.tgcStepList:
            if stepvalue.system not in syslist:
                syslist.append(stepvalue.system)

    if para_dict['restart'] == "YES":
        # resetEmma and instrEmma
        bool_ret, msg = instr_and_reset_emma(syslist, conf)

    time_start = time()
    case_list_with_testresult = DubboService().execute_group_testcases(case_list, conf, env)
    time_end = time()
    ret_dict['takeTime'] = str(time_end-time_start)


    # generate emmaReport and scp to testwebserver，并返回系统对应的web地址的覆盖率网页。
    # 初始化urldict
    url_dict = {}
    # init ret_url_dict
    for syskey in syslist:
        url_dict[syskey] = {}
        url_dict[syskey]['url'] = "None"

    if para_dict['restart'] == "YES":
        url_dict = ctl_and_report_emma(syslist, conf,para_dict['webroot'],para_dict['uri'])

    # TODO 不同系统下根据url获取网页数据并使用beautifulSoap解析出来覆盖率信息。（也可在生成报告时获取）
    #生成报告的路径下
    try:
        pass
        #TODO 暂时不执行报告，仅做数据获取和执行部分，报告生成未完成。
        result_dicts = HTML_Report().generate_report_for_group_case(case_list_with_testresult, url_dict, para_dict['report_file'])
    except Exception, e:
        logging.debug(traceback.format_exc())
        ret_dict['comments'] = u"%s%s" % (PromptMsg.reportFailAndReason,e)
        ret_dict['report_file'] = ""
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: %s" % ret_dict['comments'])
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: %s" % PromptMsg.emailNotSend)
        return ret_dict

    isError = False
    isFail = False
    isException = False
    for i in range(0,1):
        logging.debug(u"本次测试总共测试用例数量[%s]，通过[%s]，失败[%s]，错误[%s]。" % (result_dicts['count'],result_dicts['pass'],result_dicts['fail'],result_dicts['error']))
        if result_dicts['error'] > 0 :
            isError = True
            ret_dict['comments'] = ret_dict['comments'] +u'测试用例存在错误，总共测试用例数量[%s]，通过[%s]，失败[%s]，错误[%s]。\n' % (result_dicts['count'], result_dicts['pass'], result_dicts['fail'], result_dicts['error'])
            # ret_dict['exec_result'] = 3  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
        elif result_dicts['fail'] > 0:
            isFail = True
            ret_dict['comments'] = ret_dict['comments'] +u'测试未通过，总共测试用例数量[%s]，通过[%s]，失败[%s]。\n' % (result_dicts['count'],result_dicts['pass'],result_dicts['fail'])
            # ret_dict['exec_result'] = 2  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
            # if para_dict['is_send_mail'] == "YES":
            #     email_list = para_dict['mail_list'][k]
            #     title = u"Dubbo接口测试--系统%s出现失败用例%d个" % (k, result_dicts[k]['fail'])
            #     content = u"详情见附件测试报告。"
            #     for i in range(0, 10):
            #         try:
            #             UsualTools.send_mail(email_list, title, content, para_dict['report_file'])
            #             # is_send_mail_send = True
            #             break
            #         except Exception, e:
            #             print u"Email发送失败，尝试再次发送。原因：%s" % e
        elif result_dicts['count'] == result_dicts['pass']:
            ret_dict['comments'] = ret_dict['comments'] +u'测试通过，总共测试用例数量[%s]，通过[%s]。\n' % (result_dicts['count'],result_dicts['pass'])
            # ret_dict['exec_result'] = 1  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
        else:
            isException = True
            ret_dict['comments'] = ret_dict['comments'] +u'测试出现异常，总共测试用例数量[%s]，通过[%s]，失败[%s]，错误[%s]。\n' % (result_dicts['count'], result_dicts['pass'], result_dicts['fail'], result_dicts['error'])
            # ret_dict['exec_result'] = 4  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION

    if isException:
        ret_dict['exec_result'] = 4
    elif isError:
        ret_dict['exec_result'] = 3
    elif isFail:
        ret_dict['exec_result'] = 2
    else:
        ret_dict['exec_result'] = 1


    logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: 任务执行完毕。")
    logging.info(u"***************************************************************************************************")
    logging.info(u"***************************************************************************************************")
    return ret_dict

def run_platform_http_task(para_dict={}):
    """执行测试用例，并生成测试报告。
    """
    ret_dict = {}
    ret_dict['takeTime'] = '0'
    ret_dict['comments'] = u''
    ret_dict['exec_result'] = 4 # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
    ret_dict['report_file'] = para_dict['report_file']

    case_list = para_dict['case_list']
    conf = para_dict['conf']
    env = para_dict['env']
    result_dicts = {}
    if len(case_list) == 0:
        ret_dict['comments'] = PromptMsg.noneCaseFail
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_http_task: %s" % ret_dict['comments'])
        return ret_dict
    logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_http_task: case_list长度:%s" % len(case_list))
    time_start = time()
    case_list_with_testresult = HttpService().execute_testcases(case_list, conf, env)
    time_end = time()
    ret_dict['takeTime'] = str(time_end-time_start)

    # generate emmaReport and scp to testwebserver，并返回系统对应的web地址的覆盖率网页。
    # 初始化urldict
    # TODO 不同系统下根据url获取网页数据并使用beautifulSoap解析出来覆盖率信息。（也可在生成报告时获取）
    #生成报告的路径下
    try:
        result_dicts = HTML_Report().generate_report_for_http (case_list_with_testresult, para_dict['report_file'])
        #TODO 生成报告后写入数据库报告文件地址。
    except Exception, e:
        ret_dict['comments'] = u"%s%s" % (PromptMsg.reportFailAndReason, e)
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: %s" % ret_dict['comments'])
        logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_dubbo_task: %s" % PromptMsg.emailNotSend)
        return ret_dict
    finally:
        if result_dicts['error'] > 0:
            ret_dict['comments'] = u'ERROR：测试未通过，总共测试用例数量[%s]，有错误用例[%s]。' % (result_dicts['total'], result_dicts['error'])
            ret_dict['exec_result'] = 3  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
        elif result_dicts['fail'] > 0:
            ret_dict['comments'] = u'FAIL：测试未通过，总共测试用例数量[%s]，通过[%s]，失败[%s]。' % (result_dicts['total'], result_dicts['pass'], result_dicts['fail'])
            ret_dict['exec_result'] = 2  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
            if para_dict['is_send_mail'] == "YES":
                email_list = para_dict['mail_list']
                title = u"HTTP接口测试--系统%s出现失败用例%d个" % (result_dicts['fail'])
                content = u"详情见附件测试报告。"
                for i in range(0, 10):
                    try:
                        UsualTools.send_mail(email_list, title, content, para_dict['report_file'])
                        # is_send_mail_send = True
                        break
                    except Exception, e:
                        print u"Email发送失败，尝试再次发送。原因：%s" % e
        elif result_dicts['total'] == result_dicts['pass']:
            ret_dict['comments'] = u'PASS：测试通过，总共测试用例数量[%s]，通过[%s]，失败[%s]。' % (result_dicts['total'], result_dicts['pass'], result_dicts['fail'])
            ret_dict['exec_result'] = 1  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION
        else:
            ret_dict['comments'] = u'测试出现异常，总共测试用例数量[%s]，通过[%s]，失败[%s]，错误[%s]。' % (
                result_dicts['total'], result_dicts['pass'], result_dicts['fail'], result_dicts['error'])
            ret_dict['exec_result'] = 4  # 1 PASS 2 FAIL 3 ERROR 4 EXCEPTION

    logging.info(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: run_platform_http_task: 任务执行完毕。")
    logging.info(u"***************************************************************************************************")
    logging.info(u"***************************************************************************************************")
    return ret_dict

def getConfFromDB(db, confKey, confPath='tmp.conf'):
    os.system("rm -rf %s" % confPath)
    ####===========生成配置文件Start=================================================================
    retConf = {}
    retConfDict = {}
    # step 1 获取配置文件
    confSql = "select confText from tb_conf where state=1 and confName='%s'" % confKey
    confRes = db.execute_sql(confSql)
    logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfFromDB: 从数据库获取的confText为：%s。" % confRes)
    if confRes:
        try:
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfFromDB: confRes[0][0]:%s。" % confRes[0][0])
            file_object = ''
            file_object = open(confPath, 'w')
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfFromDB: file_object opened!!。")
            file_object.write(confRes[0][0])
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfFromDB: file_object writed!!。")
            file_object.flush()
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfFromDB: file_object flushed!!。")
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfFromDB: 成功写入文件！")
            retConfDict = Config(confPath)
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfFromDB: 生成配置成功！")
            retConf['errorCode'] = '10000'
            retConf['errorMsg'] = 'ok'
            # os.remove(confPath) #此行报错
        except Exception, exc:
            tmpText = u"配置文件写失败，请联系管理员检查confPath:%s。异常信息：%s" % (confPath, exc)
            retConf['errorCode'] = '10001'
            retConf['errorMsg'] = tmpText
        finally:
            if type(file_object) == types.FileType:
                file_object.close()

            os.system("rm -rf %s" % confPath)
            return retConf, retConfDict
    else:
        tmpText = u"找不到配置文件，请联系管理员查看系统的key：%s。" % confKey
        retConf['errorCode'] = '10002'
        retConf['errorMsg'] = tmpText
        return retConf, retConfDict
        ####===========生成配置文件END===================================================================

def getConfigObj(confKey, confText, confPath='tmp.conf'):
    os.system("rm -rf %s" % confPath)
    ####===========生成配置文件Start=================================================================
    retConf = {}
    retConfDict = {}
    # step 1 获取配置文件
    if confText!="":
        try:
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfigObj: confRes[0][0]:%s。" % confText)
            file_object = ''
            file_object = open(confPath, 'w')
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfigObj: file_object opened!!。")
            file_object.write(confText)
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfigObj: file_object writed!!。")
            file_object.flush()
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfigObj: file_object flushed!!。")
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfigObj: 成功写入文件！")
            retConfDict = Config(confPath)
            logging.debug(UsualTools().get_current_time() + u"=>runWebPlatformFunc.py: getConfFromDB: 生成配置成功！")
            retConf['errorCode'] = '10000'
            retConf['errorMsg'] = 'ok'
            # os.remove(confPath) #此行报错
        except Exception, exc:
            tmpText = u"配置文件写失败，请联系管理员检查confPath:%s。异常信息：%s" % (confPath, exc)
            retConf['errorCode'] = '10001'
            retConf['errorMsg'] = tmpText
        finally:
            if type(file_object) == types.FileType:
                file_object.close()
            os.system("rm -rf %s" % confPath)
            return retConf, retConfDict
    else:
        tmpText = u"找不到配置文件，请联系管理员查看系统的key：%s。" % confKey
        retConf['errorCode'] = '10002'
        retConf['errorMsg'] = tmpText
        return retConf, retConfDict
        ####===========生成配置文件END===================================================================


if __name__ == "__main__":
    #根据PARAM设定输出log的级别和保存文件。
    logging.basicConfig(level="DEBUG",
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename="t.log",
                        filemode='w')
    retbool,retstring = instr_and_reset_emma(["stock"], Config("../ConfFile/dev.conf"))
    print retbool
    print retstring
    ret_dict = ctl_and_report_emma(["stock"], Config("../ConfFile/dev.conf"))
    print ret_dict