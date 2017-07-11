# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""

import sys, os, logging,paramiko


reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

from ExcelProcess.ExcelProcess import ExcelProcess
from ExcelProcess.ExcelForHttpProcess import ExcelForHttpProcess
from DubboService.DubboService import DubboService
from DubboService.HttpService import HttpService
from ResultProcess.HTML_Report import HTML_Report


from Config.Config import Config
from time import time,sleep
from Lib.UsualTools import UsualTools
from Lib.VerifyTool import VerifyTool
from Config.GlobalConf import ServiceConf

#==========================DUBBO=====START=====================================
def run_all(filepath="Testcases/", para_dict={}):
    """执行所有Testcases/目录下的所有xlsx文件，并生成测试报告到reports目录下。

    :param filepath:
    :param report_path:
    :param conf:
    :return:
    """
    confpath = para_dict['confpath']

    if os.path.exists(filepath) and os.path.isdir(filepath):
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_all: 执行%s下所有用例。" % filepath)
        # 'testcase', pattern='Testcase*.xlsx'
        filepath = filepath[-1:] == '/' and filepath or filepath+'/'
        list_all_xlsx = [filepath + i for i in os.listdir(filepath)]
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_all: 执行文件列表：%s " % list_all_xlsx)
        run_suites(list_all_xlsx, para_dict)
    else:
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_all: 文件夹%s不存在，测试终止。" % filepath)

def run_suites(file_list=["Testcases/test.xlsx"], para_dict={}):
    """执行单个xlsx文件，并生成测试报告到reports目录下。

    :param file_list:
    :param report_path:
    :param conf:
    :return:
    """
    confpath = para_dict['confpath']
    for i in range(0, len(file_list)):
        filepath = file_list[i]  # 获取文件路径 通过参数传递或者Config默认配置
        if os.path.isfile(filepath):
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_suites: 开始执行用例文件%s".encode("utf8") % filepath)
            run_cases(filepath,para_dict)
        else:
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_suites: 用例文件%s不存在，此套件测试终止。" % filepath)

def run_cases(file="TestcasesForDubbo/Testcases_stock.xlsx",para_dict={}):
    """执行单个测试用例，并生成测试报告到reports目录下。

    :param file: 1/默认不传,那么就是运行Testcases目录下的所有用例excel文件,并一一生成报告.2/传递多个文件用,间隔.3/传递一个只要写入名字即可.
    :param case_line_list: 1/默认不传,或者传递 null或者非数字均代表之行所有Excel中用例.2/传递多个line值用,间隔.3/只传递一个值就执行单一用例.此参数只在file为单一文件时生效.
    :param report_path:1/不传就使用默认参数存入到reports目录下 2/传递路径如果非法不存在此目录提示用户并终止执行.
    :param conf:1/不传默认使用test配置.2/可传递参数时test dev stage,对应家在相应的conf文件.
    :return:
    """

    case_line_list = para_dict['case_line_list']
    report_path = para_dict['report_path']
    conf = para_dict['conf']
    env = para_dict['env']
    is_send_mail = para_dict['is_send_mail'] == "YES" and True or False
    mail_list = para_dict['mail_list']
    confpath = para_dict['confpath']
    report_filename = para_dict['report_filename']

    result_dicts = {}
    if os.path.exists(file) and os.path.isfile(file):
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: 开始执行用例文件%s ".encode('utf8') % file)
        filepath = file  # 获取文件路径 通过参数传递或者Config默认配置
        time_before_get_case_list = time()
        case_list = []
        try:
            case_list = ExcelProcess().get_case_list(filepath, case_line_list)
        except Exception, e:
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: ExcelProcess().get_case_list调用失败：%s" % e)
        time_after_get_case_list = time()
        if len(case_list) == 0:
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases:用例列表获取失败！程序退出！")
            sys.exit(0)
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: ExcelProcess().get_case_list函数占用时间:%s" % str(time_after_get_case_list - time_before_get_case_list))
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: case_list长度:%s" % len(case_list))

        time_before_execute_testcases = time()

        #根据case_list生成系统list
        syslist = []
        for casevalue in case_list:
            if casevalue['system'] not in syslist:
                syslist.append(casevalue['system'])

        if para_dict['restart'] == "YES":
            #resetEmma and instrEmma
            bool_ret,msg = instr_and_reset_emma(syslist,conf)

        case_list_with_testresult = DubboService().execute_testcases(case_list, conf, env)
        #generate emmaReport and scp to testwebserver，并返回系统对应的web地址的覆盖率网页。
        #初始化urldict
        url_dict = {}
        # init ret_url_dict
        for syskey in syslist:
            url_dict[syskey] = {}
            url_dict[syskey]['url'] = "None"

        if para_dict['restart'] == "YES":
            url_dict = ctl_and_report_emma(syslist,conf)

        #TODO 不同系统下根据url获取网页数据并使用beautifulSoap解析出来覆盖率信息。（也可在生成报告时获取）

        time_after_execute_testcases = time()
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: DubboService().execute_testcases函数占用时间:%s" % str(
            time_after_execute_testcases - time_before_execute_testcases))

        logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: case_list_with_testresult长度：%s" % len(case_list_with_testresult))
        file_name_list = file.split('/')
        report_path = report_path[-1:] == '/' and report_path or report_path + '/'
        report_file = report_filename=='' and "Report_%s.html" % file_name_list[len(file_name_list) - 1] or report_filename
        report_file = report_path + report_file
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: 用例文件[%s]执行后报告文件路径: %s".encode('utf8') % (file,report_file))
        time_before_generate_excel_test_report = time()
        try:
            result_dicts = HTML_Report().generate_report(case_list_with_testresult,url_dict,report_file)
            time_after_generate_excel_test_report = time()
            logging.info(
                UsualTools().get_current_time() + u"=>run.py: run_cases: rp.generate_excel_test_report函数占用时间:%s" % str(
                    time_after_generate_excel_test_report - time_before_generate_excel_test_report))
            logging.info(UsualTools().get_current_time() + u"=>run.py: run_cases: 用例文件[%s]执行完成!".encode('utf8') % file)
        except Exception, e:
            logging.info(u"测试报告生成失败,原因：%s" % e)
            logging.info("EMAIL_NOT_SEND")
            print "EMAIL_NOT_SEND"
            if mail_list != "":
                for i in range(0, 10):
                    try:
                        UsualTools.send_mail(mail_list, u"HTTP接口测试报告", u"报告生成失败，已发送错误原因到管理员，请耐心等待。","")
                        UsualTools.send_mail(['wangjiliang@mftour.cn'], u"HTTP接口测试报告生成失败，请查看原因", u"报告[%s]生成失败，原因：%s。出错邮箱列表：%s" % (report_file,e,mail_list),"")
                        is_mail_list_send = True
                        break
                    except Exception, e:
                        print u"Email发送失败，尝试再次发送。原因：%s" % e
            sys.exit()

        #发送邮件这里
        #is_send_mail_send = False
        is_mail_list_send = False
        if is_send_mail:
            for k,v in result_dicts.items():
                if type(v) != type({}) : continue
                if v['fail'] > 0:
                    email_list = conf.conf_dict[k]['email_list']
                    title = u"Dubbo接口测试--系统%s出现失败用例%d个" % (k,result_dicts[k]['fail'])
                    content = u"详情见附件测试报告。"
                    for i in range(0,10):
                        try:
                            UsualTools.send_mail(email_list,title,content,report_file)
                            #is_send_mail_send = True
                            break
                        except Exception, e:
                            print u"Email发送失败，尝试再次发送。原因：%s" % e
        if mail_list!="":
            for i in range(0, 10):
                try:
                    UsualTools.send_mail(mail_list, u"Dubbo接口测试报告", u"详情见附件。", report_file)
                    is_mail_list_send = True
                    break
                except Exception, e:
                    print u"Email发送失败，尝试再次发送。原因：%s" % e

        #第一阶段，必须有mail_list去接收报告才算测试完成。
        if mail_list!="" and is_mail_list_send:
            #发送email成功
            logging.info("TEST_FINISHED")
            print "TEST_FINISHED"
        else:
            # 发送email成功
            logging.info("EMAIL_NOT_SEND")
            print "EMAIL_NOT_SEND"

    else:
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: 用例文件%s不是文件或者不存在，终止执行。" % file)
    logging.info( u"***************************************************************************************************")
    logging.info( u"***************************************************************************************************")
    logging.info( u"***************************************************************************************************")

def instr_and_reset_emma( syslist = ["stock","sku","trade"], conf = Config("../Config/dev.conf") ):
    """
    重置emma，并重新插装。
    最好是重启系统。
    :param syslist:
    :param conf:
    :return:
    """
    tmp_dir = "/home/wangjiliang";
    for value in syslist:
        ip = conf.conf_dict[value]['host_addr']
        port = int(conf.conf_dict[value]['ssh_port'])
        username = conf.conf_dict[value]['ssh_user']
        password = conf.conf_dict[value]['ssh_passwd']
        base_dir = conf.conf_dict[value]['base_dir']

        telnet_port = conf.conf_dict[value]['host_port']

        try:
            # 生成ssh客户端实例
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(ip, port, username, password,timeout=10)

            #获取插装jar列表。
            stdin, stdout, stderr = s.exec_command("ls %s/lib | grep %s-dao-" % (base_dir, value))
            libdaostr = stdout.read().strip()
            #print libdaostr
            stdin, stdout, stderr = s.exec_command("ls %s/lib | grep %s-service-" % (base_dir, value))
            libservicestr = stdout.read().strip()
            #print libservicestr
            stdin, stdout, stderr = s.exec_command("ls %s/lib | grep %s-engine-" % (base_dir, value))
            libenginestr = stdout.read().strip()
            #print libenginestr
            instr_jar_final_str = "%s/lib/%s,%s/lib/%s,%s/lib/%s" % (base_dir,libdaostr,base_dir,libenginestr,base_dir,libservicestr)
            #生成shelllist string。
            shell_list = """source /etc/profile;
cd %s/bin;
./stop.sh;
rm -rf %s/log/test.em;
#recover lib start.
cd %s;
rm -rf lib/*;
cp -rf libbak/* lib/;
#recover lib end.
java emma instr -m overwrite -cp  %s -ix +com.pzj.* -Dmetadata.out.file=%s/log/test.em;
cd %s/bin;
./startup.sh;""" % (base_dir, tmp_dir, base_dir, instr_jar_final_str, tmp_dir, base_dir)
            #开始执行shell命令 先加载环境变量
            stdin, stdout, stderr = s.exec_command("cd %s;rm -rf tinstr.sh;echo '%s' > tinstr.sh;chmod +x tinstr.sh;" % (tmp_dir,shell_list))
            geneshstr = stdout.read()
            stdin, stdout, stderr = s.exec_command("cd %s;ls;" % tmp_dir)
            lsstr = stdout.read()
            if "tinstr.sh" not in lsstr:
                logging.debug( "ERROR: tinstr.sh not generate!")
                return False,"ERROR: [%s]tinstr.sh not generate!" % value
            stdin, stdout, stderr = s.exec_command("cd %s;./tinstr.sh;" % tmp_dir)
            emmastartstr = stdout.read()
            if "EMMA: processing instrumentation path" not in emmastartstr:
                logging.debug( "ERROR: No EMMA instr executed!")
                return False, "ERROR: [%s]No EMMA instr executed!" % value

            logging.debug( "%s started." % value)

            #java进程是否启动
            isJavaStarted = False
            for i in range(0,10):
                stdin, stdout, stderr = s.exec_command("ps -ef |grep java")
                return_value =  stdout.read()
                logging.debug( return_value)
                if libservicestr in return_value:
                    logging.debug( "java started successful!")
                    isJavaStarted = True
                    break
                else:
                    sleep(2)

            if isJavaStarted == False:
                return False, "ERROR: [%s]java started FAIL! LOG:%s" % (value,return_value)

            #检测端口是否可用
            isPort20880Listened = False
            for i in range(0, 10):
                stdin, stdout, stderr = s.exec_command("netstat -anp --ip |grep 0.0.0.0:%s |grep LISTEN" % telnet_port)
                return_value = stdout.read()
                logging.debug(return_value)
                if ("0.0.0.0:%s" % telnet_port) in return_value:
                    logging.debug("telnet service on port %s started successful!" % telnet_port)
                    isPort20880Listened = True
                    break
                else:
                    sleep(2)

            if isPort20880Listened == False:
                return False, "ERROR: [%s]telnet service on port %s started FAIL! LOG:%s" % (value,telnet_port, return_value)

            stdin, stdout, stderr = s.exec_command("netstat -anp --ip |grep 47653")
            return_value = stdout.read()
            logging.debug( return_value)
            if ":47653" in return_value:
                logging.debug( "EMMA instr started successful!")
            else:
                logging.debug( "EMMA instr FAIL!")
                return False, "ERROR: [%s]EMMA instr FAIL! LOG:%s" % (value,return_value)
            s.close()
        except Exception,e:
            logging.debug(UsualTools().get_current_time() + u"=>run.py: ctl_and_report_emma: 发生异常。MSG:%s" % e)
            return False,u"发生异常：%s" % e
    return True,"SUCCESS"

def ctl_and_report_emma( syslist = ["stock","sku","trade"], conf = Config("../Config/dev.conf"),webroot = '/data/tp/test/InterfaceTestFrameworkWeb/webroot', uri = 'http://10.0.18.31' ):
    """
    重置emma，并重新插装。
    最好是重启系统。
    :param syslist:
    :param conf:
    :return:
    """
    ret_url_dict={}
    #init ret_url_dict
    for syskey in syslist:
        ret_url_dict[syskey]={}
        ret_url_dict[syskey]['url']="None"
    tmp_dir = "/home/wangjiliang";
    for value in syslist:
        ip = conf.conf_dict[value]['host_addr']
        port = int(conf.conf_dict[value]['ssh_port'])
        username = conf.conf_dict[value]['ssh_user']
        password = conf.conf_dict[value]['ssh_passwd']
        base_dir = conf.conf_dict[value]['base_dir']

        # java_src = conf.conf_dict[value]['java_src']
        # java_src_list = java_src.split(',')
        # java_src_final_str = ""
        # for srcvalue in java_src_list:
        #     java_src_final_str += "%s%s," % (base_dir, srcvalue)
        # java_src_final_str = java_src_final_str[:-1]

        java_src_final_str = "%s/%s/%s-dao/src/main/java,%s/%s/%s-engine/src/main/java,%s/%s/%s-service/src/main/java" % (base_dir,value,value,base_dir,value,value,base_dir,value,value)

        ctime = UsualTools.get_current_time_numstr()
        renamereportpath = "reportfor%s%s" % (value,ctime)
        shell_list = """source /etc/profile;
cd %s;
rm -rf log/test.ec;
java emma ctl -connect localhost:47653 -command coverage.get,log/test.ec;
#generate report html
rm -rf report/*;
#-sp /xxxx/xxxx/javaSources  report have src
java emma report -r html -sp %s -in log/test.em,log/test.ec -Dreport.html.out.file=report/test.html;
#copy to webserver
cp -r report %s;
scp -P50022 -r %s root@10.0.18.31:%s/emma/%s/;
rm -rf reportfor*;
""" % (tmp_dir,java_src_final_str,renamereportpath,renamereportpath,webroot,value)
        try:
            # 生成ssh客户端实例
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(ip, port, username, password,timeout=10)

            #初始化环境变量
            #开始执行shell命令 先加载环境变量
            stdin, stdout, stderr = s.exec_command("cd %s;rm -rf tctlreportcp.sh;echo '%s' > tctlreportcp.sh;chmod +x tctlreportcp.sh;" % (tmp_dir,shell_list))
            geneshstr = stdout.read()
            stdin, stdout, stderr = s.exec_command("cd %s;ls;" % tmp_dir)
            lsstr = stdout.read()
            if "tctlreportcp.sh" not in lsstr:
                logging.debug( "ERROR: tctlreportcp.sh not generate!")
            stdin, stdout, stderr = s.exec_command("cd %s;./tctlreportcp.sh;" % tmp_dir)
            emmactlstr = stdout.read()

            if "EMMA: coverage.get: command completed in" in emmactlstr and "writing [html] report to [/home/wangjiliang/report/test.html]" in emmactlstr:
                url = "%s/emma/%s/%s/test.html" % (uri,value,renamereportpath)
                logging.debug( "SUCCESS: REPORT generate and send to remote webserver. report url:%s" % url)
                ret_url_dict[value]['url']=url
            else:
                logging.debug( "ERROR: REPORT generate failed; LOG:%s" % emmactlstr)
            s.close()
        except Exception,e:
            logging.debug(UsualTools().get_current_time() + u"=>run.py: ctl_and_report_emma: 发生异常。MSG:%s" % e)
    return ret_url_dict


#==========================DUBBO=====END=======================================

#***********************************************************************************************************************************

#=====================HTTP====START=======================
def run_http_all(filepath="TestcasesForHttp/",para_dict={}):
    """执行所有Testcases/目录下的所有xlsx文件，并生成测试报告到reports目录下。

    :param filepath:
    :param report_path:
    :param conf:
    :return:
    """

    if os.path.exists(filepath) and os.path.isdir(filepath):
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_all: 执行%s下所有用例。" % filepath)
        # 'testcase', pattern='Testcase*.xlsx'
        filepath = filepath[-1:] == '/' and filepath or filepath+'/'
        list_all_xlsx = [filepath + i for i in os.listdir(filepath)]
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_all: 执行文件列表：%s " % list_all_xlsx)
        run_http_suites(list_all_xlsx,para_dict)
    else:
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_all: 文件夹%s不存在，测试终止。" % filepath)

def run_http_suites(file_list=["TestcasesForHttp/Testcases_http.xlsx"],para_dict={} ):
    """执行单个xlsx文件，并生成测试报告到reports目录下。
    :param file_list:
    :param report_path:
    :param conf:
    :return:
    """

    for i in range(0, len(file_list)):
        filepath = file_list[i]  # 获取文件路径 通过参数传递或者Config默认配置
        if os.path.isfile(filepath):
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_suites: 开始执行用例文件%s".encode("utf8") % filepath)
            run_http_cases(filepath, para_dict)
        else:
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_suites: 用例文件%s不存在，此套件测试终止。" % filepath)

def run_http_cases(file="TestcasesForHttp/Testcases_http.xlsx", para_dict ={}):
    """执行单个测试用例，并生成测试报告到reports目录下。

    :param file: 1/默认不传,那么就是运行Testcases目录下的所有用例excel文件,并一一生成报告.2/传递多个文件用,间隔.3/传递一个只要写入名字即可.
    :param case_line_list: 1/默认不传,或者传递 null或者非数字均代表之行所有Excel中用例.2/传递多个line值用,间隔.3/只传递一个值就执行单一用例.此参数只在file为单一文件时生效.
    :param report_path:1/不传就使用默认参数存入到reports目录下 2/传递路径如果非法不存在此目录提示用户并终止执行.
    :param conf:1/不传默认使用test配置.2/可传递参数时test dev stage,对应家在相应的conf文件.
    :return:
    """

    case_line_list = para_dict['case_line_list']
    report_path = para_dict['report_path']
    conf = para_dict['conf']
    env = para_dict['env']
    is_send_mail = para_dict['is_send_mail'] == "YES" and True or False
    mail_list = para_dict['mail_list']
    confpath = para_dict['confpath']
    report_filename = para_dict['report_filename']

    result_dicts = {}
    if os.path.exists(file) and os.path.isfile(file):
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: 开始执行用例文件%s ".encode('utf8') % file)
        filepath = file  # 获取文件路径 通过参数传递或者Config默认配置
        time_before_get_case_list = time()
        case_list = []
        try:
            case_list = ExcelForHttpProcess().get_case_list(filepath, case_line_list)
        except Exception, e:
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: ExcelProcess().get_case_list调用失败：%s" % e)
        time_after_get_case_list = time()
        if len(case_list) == 0:
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases:用例列表获取失败！程序退出！")
            sys.exit(0)
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: ExcelForHttpProcess().get_case_list函数占用时间:%s" % str(time_after_get_case_list - time_before_get_case_list))
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: case_list长度:%s" % len(case_list))

        time_before_execute_testcases = time()
        logging.debug(u"confpath in run_http_cases: %s" % confpath)
        case_list_with_testresult = HttpService().execute_testcases(case_list , conf,env)
        time_after_execute_testcases = time()
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: DubboService().execute_testcases函数占用时间:%s" % str(
            time_after_execute_testcases - time_before_execute_testcases))

        logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: case_list_with_testresult长度：%s" % len(case_list_with_testresult))

        file_name_list = file.split('/')
        report_path = report_path[-1:] == '/' and report_path or report_path + '/'
        report_file = report_filename=='' and "Report_%s.html" % file_name_list[len(file_name_list) - 1] or report_filename
        report_file = report_path + report_file
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: 用例文件[%s]执行后报告文件路径: %s".encode('utf8') % (file,report_file))
        time_before_generate_excel_test_report = time()
        try:
            result_dicts = HTML_Report().generate_report_for_http(case_list_with_testresult,report_file)
            time_after_generate_excel_test_report = time()
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: rp.generate_excel_test_report函数占用时间:%s" % str(
                time_after_generate_excel_test_report - time_before_generate_excel_test_report))
            logging.info( UsualTools().get_current_time() + u"=>run.py: run_http_cases: 用例文件[%s]执行完成!".encode('utf8') % file)
        except Exception, e:
            logging.info(u"测试报告生成失败,原因：%s" % e)
            logging.info("EMAIL_NOT_SEND")
            if mail_list != "":
                for i in range(0, 10):
                    try:
                        UsualTools.send_mail(mail_list, u"HTTP接口测试报告", u"报告生成失败，已发送错误原因到管理员，请耐心等待。","")
                        UsualTools.send_mail(['wangjiliang@mftour.cn'], u"HTTP接口测试报告生成失败，请查看原因", u"报告[%s]生成失败，原因：%s。出错邮箱列表：%s" % (report_file,e,mail_list),"")
                        is_mail_list_send = True
                        break
                    except Exception, e:
                        print u"Email发送失败，尝试再次发送。原因：%s" % e
            print "EMAIL_NOT_SEND"
            sys.exit()

        # result_dicts = HTML_Report().generate_report_for_http(case_list_with_testresult, report_file)
        # time_after_generate_excel_test_report = time()
        # logging.info(
        #     UsualTools().get_current_time() + u"=>run.py: run_http_cases: rp.generate_excel_test_report函数占用时间:%s" % str(
        #         time_after_generate_excel_test_report - time_before_generate_excel_test_report))
        # logging.info(UsualTools().get_current_time() + u"=>run.py: run_http_cases: 用例文件[%s]执行完成!".encode('utf8') % file)

        #发送邮件这里
        is_send_mail_send=False
        is_mail_list_send=False
        if is_send_mail:
            if result_dicts['fail'] > 0 :
                email_list = Config(confpath=='' and "../Config/http.conf" or confpath+"/Config/http.conf").conf_dict[env]['email_list']
                title = u"HTTP接口测试报告"
                content = u"详情见附件测试报告。"
                for i in range(0, 10):
                    try:
                        UsualTools.send_mail(email_list, title, content, report_file)
                        break
                    except Exception, e:
                        print u"Email发送失败，尝试再次发送。原因：%s" % e
        if mail_list!="":
            for i in range(0, 10):
                try:
                    UsualTools.send_mail(mail_list, u"HTTP接口测试报告", u"详情见附件。", report_file)
                    is_mail_list_send = True
                    break
                except Exception, e:
                    print u"Email发送失败，尝试再次发送。原因：%s" % e

        # 第一阶段，必须有mail_list去接收报告才算测试完成。
        if mail_list != "" and is_mail_list_send:
            # 发送email成功
            logging.info("TEST_FINISHED")
            print "TEST_FINISHED"
        else:
            # 发送email成功
            logging.info("EMAIL_NOT_SEND")
            print "EMAIL_NOT_SEND"

    else:
        logging.info( UsualTools().get_current_time() + u"=>run.py: run_cases: 用例文件%s不是文件或者不存在，终止执行。" % file)
    logging.info( u"***************************************************************************************************")
    logging.info( u"***************************************************************************************************")
    logging.info( u"***************************************************************************************************")
#=====================HTTP====END=========================
#***********************************************************************************************************************************
#=========================参数数据处理===开始============================
def init_sys_argv(arg_string):
    """初始化参数传递
    参数列表表达式:file=test.xlsx;case_line_list=1,2,3,4,5,8-11,14;report_path=../reports;conf=test;email=wangjiliang@mftour.cn,liyachao@mftour.cn;
    file:
        1/默认不传,那么就是运行Testcases目录下的所有用例excel文件,执行run_all.
        2/传递目录,执行传递目录的所有Excel,即调用run_all.使用os判断参数是否为目录
        3/传递多个文件用,间隔,生成list并执行run_suite.
        4/传递一个Excel那么执行run_cases.使用os判断是否为有效文件.
    case_line_list: 当参数1 file到分支4时,此参数才有意义,不然可传''/null/0.
        1/默认不传,或者传''/null/0.
        2/传递多个line值用,间隔.例如: 1,3,5,6,7,10-15,18, 10-15表示10,11,12,13,14,15行
        3/只传递一个值就执行单一用例.例如:4  就是只执行第四行用例
    report_path: 报告存放路径
        1/不传就使用默认参数存入到reports目录下
        2/传递路径如果非法不存在此目录提示用户并终止执行.
    conf:
        1/不传默认使用test.conf配置.
        2/可传递参数时test dev stage,对应加载相应的conf文件.
    """

    param_dict = {}
    param_dict['protocol'] = 'DUBBO'
    param_dict['file'] = 'Testcases/'
    param_dict['report_path'] = 'reports'
    param_dict['conf'] = 'test'
    param_dict['loglevel'] = 'INFO'
    param_dict['logfile'] = 'test.log'
    param_dict['is_send_mail'] = 'NO'
    param_dict['restart'] = 'YES'
    if arg_string!="":
        params_str = arg_string #sys.argv[1]
        # params_str = "file=test.xlsx;case_line_list=1,2,3,4,5,8-11,14;report_path=../reports;conf=test;email=wangjiliang@mftour.cn,liyachao@mftour.cn;"
        params_list = params_str.split("--")
        for param in params_list:
            if param != '':
                if 'report_filename=' in param or 'confpath=' in param or 'protocol=' in param or 'file=' in param or 'case_line_list=' in param or 'report_path=' in param or 'conf=' in param or 'is_send_mail=' in param or 'mail_list=' in param or 'loglevel=' in param or 'logfile=' in param or 'restart=' in param :
                    param_list = param.split("=")
                    if len(param_list) == 2:
                        param_dict[param_list[0]] = param_list[1]
                    else:
                        print UsualTools().get_current_time() + u"=>run.py: init_sys_argv: 参数格式错误，%s未发现=号。参数示例：file=test.xlsx--case_line_list=1,2,3,4,5,8-11,14--report_path=../reports--conf=test" % param
                        sys.exit(0)
                else:
                    print UsualTools().get_current_time() + u"=>run.py: init_sys_argv: 详细参数错误，只能是report_filename/file/case_line_list/report_path/conf/email/loglevel/logfile/restart。示例：参数示例：file=test.xlsx--case_line_list=1,2,3,4,5,8-11,14--report_path=../reports--conf=test--restart=NO"
                    sys.exit(0)
    else:
        print UsualTools().get_current_time() + u"=>run.py: init_sys_argv: 参数为空，使用默认值。"

    return param_dict

def process_init_param_dict(param_dict):
    return_param_dict = {}

    # process file
    try:
        proto = param_dict['protocol']
        #print u"run.py: process_init_param_dict: %s" % file
        if proto == "DUBBO" or proto == "HTTP" :
            return_param_dict['protocol'] =  proto
        else:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: protocol参数只能是DUBBO/HTTP！"
            sys.exit(0)
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数protocol，设置为默认值[DUBBO]。"
        return_param_dict['protocol'] = "DUBBO"

    # process file
    try:
        file = param_dict['file']
        #print u"run.py: process_init_param_dict: %s" % file
        if os.path.isdir(file):
            # 传入目录
            return_param_dict['file'] = file
        else:
            # 不是目录
            file_list = file.split(',')
            for filepath in file_list:
                isFile = os.path.isfile(filepath)
                print filepath
                print isFile
                if isFile == False:
                    print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 传入的用例文件或者目录不合法，请确认路径！传入的路径为%s" % filepath
                    sys.exit(0)
            return_param_dict['file'] = file_list
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数file，设置为默认值[Testcases/]。"
        return_param_dict['file'] =  proto=="DUBBO" and "TestcasesForDubbo/" or "TestcasesForHttp/"

    # process case_line_list
    try:
        case_line_list = param_dict['case_line_list']
        return_list = []
        if case_line_list == '':
            return_list = []
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: case_line_list是空,设置为默认值[]."
        else:
            # case_line_list不为空
            case_line_list_list = case_line_list.split(',')
            for item in case_line_list_list:
                # 先看是否能转换为数字
                try:
                    if int(item) >= 2:
                        return_list.append(int(item))
                    else:
                        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 参数传递错误：case_line_list存在小于2的行数，不合法！" % item
                        sys.exit(0)
                except Exception, e2:
                    # 不能转换为数字
                    range_num_list = item.split('to')
                    if len(range_num_list) == 2:
                        try:
                            if int(range_num_list[0]) < int(range_num_list[1]) and int(range_num_list[0]) > 1:
                                # 合法，生成数字加入list
                                for i in range(int(range_num_list[0]), int(range_num_list[1]) + 1):
                                    return_list.append(i)
                            else:
                                print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 参数传递错误：case_line_list存在不符合规则的值，范围行2到行5，请使用2to5！"
                                sys.exit(0)
                        except Exception, e3:
                            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 参数传递错误：case_line_list存在不符合规则的值，范围行2到行5，请使用2to5！"
                            sys.exit(0)
                    else:
                        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 参数传递错误：case_line_list存在不符合规则的值，范围行2到行5，请使用2to5！"
                        sys.exit(0)
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数case_line_list，设置为默认值[]。"
        return_list = []
    finally:
        return_param_dict['case_line_list'] = sorted(list(set(return_list)))

    # process report_path
    try:
        report_path = param_dict['report_path']
        if os.path.isdir(report_path):
            return_param_dict['report_path'] = report_path
        else:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 报告存放目录不存在，准备创建目录。"
            try:
                os.makedirs(report_path)
                return_param_dict['report_path'] = report_path
                print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 创建报告存放目录成功。"
            except Exception, e:
                print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 报告存放目录创建失败，请检查report_path参数[%s]" % report_path
                sys.exit(0)
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数report_path，设置为默认值reports。"
        return_param_dict['report_path'] = 'reports'

    # process report_filename
    try:
        report_filename = param_dict['report_filename'].strip()
        if report_filename.lower().endswith(".html") or report_filename.lower().endswith(".htm") or report_filename=='':
            return_param_dict['report_filename'] = report_filename
        else:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 报告文件必须是.html或者.htm文件，请检查report_filename参数[%s]" % report_filename
            sys.exit(0)
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数report_filename，设置为默认值''。"
        return_param_dict['report_filename'] = ''

    # process confpath
    try:
        confpath = param_dict['confpath'].strip()
        if os.path.isdir(confpath):
            return_param_dict['confpath'] = confpath[-1:] == '/' and confpath[0:-1] or confpath
        else:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 参数confpath不是目录，设置为默认值''。"
            sys.exit(0)
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数confpath，设置为默认值''。"
        return_param_dict['confpath'] = ''

    # process conf
    if return_param_dict['protocol'] == "DUBBO":
        try:
            conf = param_dict['conf']
            if return_param_dict['confpath'] ==  "":
                if conf == 'test':
                    return_param_dict['conf'] = Config("../ConfFile/test.conf")
                    return_param_dict['env'] = "test"
                elif conf == 'dev':
                    return_param_dict['conf'] = Config("../ConfFile/dev.conf")
                    return_param_dict['env'] = "dev"
                else:
                    print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: conf参数只能是test/dev！"
                    sys.exit(0)
            else:
                if conf == 'test':
                    return_param_dict['conf'] = Config(return_param_dict['confpath']+"/ConfFile/test.conf")
                    return_param_dict['env'] = "test"
                elif conf == 'dev':
                    return_param_dict['conf'] = Config(return_param_dict['confpath']+"/ConfFile/dev.conf")
                    return_param_dict['env'] = "dev"
                else:
                    print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: conf参数只能是test/dev！"
                    sys.exit(0)
        except Exception, e:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数conf，设置为默认值test。"
            return_param_dict['conf'] = Config("../ConfFile/test.conf")
            return_param_dict['env'] = "test"
    elif return_param_dict['protocol'] == "HTTP":
        try:
            conf = param_dict['conf']
            if return_param_dict['confpath'] ==  "":
                return_param_dict['conf'] = Config("../ConfFile/http.conf")
                return_param_dict['env'] = conf
            else:
                return_param_dict['conf'] = Config(return_param_dict['confpath']+"/ConfFile/http.conf")
                return_param_dict['env'] = conf
        except Exception, e:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数conf，设置为默认值test。"
            return_param_dict['conf'] = Config("../ConfFile/http.conf")
            return_param_dict['env'] = conf

    # process is_send_mail
    try:
        is_mail = param_dict['is_send_mail']
        if is_mail == "YES" or is_mail == "NO" :
            return_param_dict['is_send_mail'] =  is_mail
        else:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: is_send_mail参数只能是YES/NO！"
            sys.exit(0)
    except Exception, e:
        print u"run.py: process_init_param_dict: 没有参数is_send_mail，设置为默认值NO。"
        return_param_dict['is_send_mail'] = "NO"

    # process mail_list   wangjilianglong@163.com,test@cc.cn,
    try:
        mail_list = param_dict['mail_list']
        #TODO 校验email
        mail_list_arr = mail_list.split(",")
        mail_list_string = ""
        for mail in mail_list_arr:
            if VerifyTool.IsEmail(mail):
                mail_list_string = mail_list_string + ";" + mail
        return_param_dict['mail_list'] =  mail_list_string
    except Exception, e:
        print u"run.py: process_init_param_dict: 没有参数mail_list，设置为默认值空。"
        return_param_dict['mail_list'] = ""

    # process loglevel INFO DEBUG
    try:
        loglevel = param_dict['loglevel']
        if loglevel == 'INFO': # or conf == 'stage':
            return_param_dict['loglevel'] = logging.INFO
        elif  loglevel == 'DEBUG':
            return_param_dict['loglevel'] = logging.DEBUG
        else:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: loglevel参数只能是INFO/DEBUG！"
            sys.exit(0)
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数loglevel，设置为默认值logging.INFO。"
        return_param_dict['loglevel'] = logging.INFO

    # process logfile
    try:
        logfile = param_dict['logfile']
        if logfile != '':
            return_param_dict['logfile'] = logfile
        else:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: logfile参数不能为空！设置为默认test.log"
            return_param_dict['logfile'] = 'test.log'
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数logfile，设置为默认值test.log。"
        return_param_dict['logfile'] = 'test.log'

    # process file
    try:
        restart = param_dict['restart']
        #print u"run.py: process_init_param_dict: %s" % file
        if restart == "YES" or restart == "NO" :
            return_param_dict['restart'] =  restart
        else:
            print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: restart参数只能是YES/NO！"
            sys.exit(0)
    except Exception, e:
        print UsualTools().get_current_time() + u"=>run.py: process_init_param_dict: 没有参数protocol，设置为默认值[DUBBO]。"
        return_param_dict['protocol'] = "DUBBO"

    return return_param_dict
#=========================参数数据处理====结束============================


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