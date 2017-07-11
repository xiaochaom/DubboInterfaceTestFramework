# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""
import sys,logging,re,random,datetime,chardet, json, time,redis

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")
import traceback
from Config.Config import Config
from Lib.DBTool import DBTool
from Lib.UsualTools import UsualTools
from Config.EncodeConf import MyEncode
from Config.GlobalConf import ServiceConf
from CommonProcess import CommonProcess
from TestcaseGroup import TestcaseGroup
from TestcaseDesc import TestcaseDesc
from TestcaseStep import TestcaseStep

class DubboService(object):
    """Dubbo接口测试底层服务
    接收用例，使用telnet方式向dubbo接口发送请求获取返回结果并存储。
    """
    def execute_testcases(self, case_list=[], config=Config("../ConfFile/test.conf"), env="test"):
        """
        获取excel数据并返回一个list，list包含N个dict，每个dict保存用例Excel中的各个值。规则如下：
        :param case_list: 一个列表，列表中每个值都是一个dict，对应的key如下。
                用例编号	名称	描述	系统	服务	方法	数据初始化	数据恢复        参数      预期结果    变量配置    (Excel列名)
                case_id     name    desc    system  service method  data_init   data_recover    params    expect      varsconf    （dict的key）
        :return: case_list_with_testresult: 一个list，主体与case_list一致，只是每个值中的dict增加key returnMsg(执行dubbo接口返回的结果)，对应的key如下。
                用例编号	名称	描述	系统	服务	方法	数据初始化	数据恢复        参数     预期结果    返回结果    (Excel列名)
                case_id     name    desc    system  service method  data_init   data_recover    params   expect      return_msg（dict的key）
        """
        cp = CommonProcess()
        logging.info( u"DubboService.py: execute_testcases: 测试环境是%s" % env)
        case_list_with_testresult = case_list

        conf = config.conf_dict
        # print conf
        logging.info(u"DubboService.py: execute_testcases: 配置是%s" % conf )
        def set_error_before_request(case_dict,err_msg):
            logging.info(u"DubboService.py: execute_testcases: %s" % err_msg)
            case_dict['return_msg'] = err_msg.encode('utf8')
            case_dict['perform_time'] = "null"
            case_dict['test_result'] = "ERROR"
            case_dict['assert_msg'] = case_dict['return_msg']
            return  case_dict
        for i in range(0, len(case_list)):
            time_start = time.time()
            logging.info(u"DubboService.py: execute_testcases: 开始执行第%d条用例。" % (i+1))
            case_list_with_testresult[i]['host'] = '0.0.0.0'
            case_list_with_testresult[i]['port'] = 8888
            case_list_with_testresult[i]['invoke_cmd'] = "No command executed!"
            case_list_with_testresult[i]['initTakeTime'] = 0.0
            case_list_with_testresult[i]['recoverTakeTime'] = 0.0
            case_list_with_testresult[i]['execTakeTime'] = 0.0
            case_list_with_testresult[i]['totalTakeTime'] = 0.0
            case_list_with_testresult[i]['perform_time'] = "null"
            case_list_with_testresult[i]['assert_msg'] = ""  # 初始化
            case_list_with_testresult[i]['return_msg'] = ""  # 初始化

            db = DBTool()
            try:
                case_id = case_list[i]['case_id'].strip()
                name = case_list[i]['name'].strip()
                desc = case_list[i]['desc'].strip()
                sys_name = case_list[i]['system'].strip()
                service_name = case_list[i]['service'].strip()
                method_name = case_list[i]['method'].strip()
                sqls_string_init = case_list[i]['data_init'].strip().strip()
                sqls_string_recover = case_list[i]['data_recover'].strip()
                params = case_list[i]['params'].strip()
                expect = case_list[i]['expect'].strip()
                varsconf = case_list[i]['varsconf'].strip()
            except Exception,e:
                case_list_with_testresult[i]=set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 读取用例数据失败，停止执行本条用例。")
                continue

            try:
                logging.info(u"DubboService.py: execute_testcases: 开始执行用例=>编号[%s]名称[%s]" % (case_id, name))
                is_sqls_string_init_executed = False
                is_get_telnet_return = False
                if case_id == '' or name == '' or desc == '' or sys_name == '' or service_name == '' or method_name == '' or sqls_string_init == '' or sqls_string_recover == '' or expect == '':
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 用例错误，有空字段，请检查用例。")
                    continue
                #用例ID校验TC_sysname_0001
                case_id_split_list = case_id.split('_')
                if len(case_id_split_list) != 3 or case_id_split_list[0] != 'TC' or case_id_split_list[1] != sys_name:
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TC_sysname_1。")
                    continue
                try:
                    if int(case_id_split_list[2]) < 1 :
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TC_sysname_0001。")
                        continue
                except Exception, e:
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TC_sysname_0001。")
                    continue
                # 校验系统名----解析系统名称------------ 在配置文件中要有
                if sys_name not in config.sections:
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 测试系统错误：当前系统%s，目前只支持如下系统%s，请检查用例。".encode('utf8') % (sys_name,config.sections))
                    continue
                #校验服务名 com.sdfsdf.sdflasd.sdklf
                if re.match('^[a-z]+[\.][a-zA-Z0-9.]+[a-zA-Z0-9]$', service_name) == None:
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 用例错误，服务不符合规则，请检查用例。服务应该类似为com.pzj.core.product.service.ScreeingsQueryService")
                    continue
                # 校验接口名字，小写字母开头，只包含字母和数字的驼峰命名法
                if re.match('^[a-z][0-9a-zA-Z]+$', method_name) == None:
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 用例错误，接口名不符合规则，请检查用例。接口名不符合规则，应该为纯字母数字组合且小写字母开头。如：queryScreeingsById")
                    continue

                #===================加载系统配置信息===============================
                logging.info( u"DubboService.py: execute_testcases: 用例所在系统是[%s]" % sys_name)
                host = conf[sys_name]['host_addr']
                port = int(conf[sys_name]['host_port'])
                logging.info( u"DubboService.py: execute_testcases: 请求地址[%s:%d]" % (host, port))
                db_host = conf[sys_name]['db_host']
                db_port = int(conf[sys_name]['db_port'])
                db_user = conf[sys_name]['db_user']
                db_pass = conf[sys_name]['db_pass']
                if host == '' or port == '' or db_host == '' or db_port == '' or db_user == '' or db_pass == '':
                    logging.info( u"DubboService.py: execute_testcases: FATAL_ERROR: 配置文件错误！终止执行！请检查配置文件是否包含当前系统的配置。")
                    sys.exit(0)
                # ----解析系统名称和配置文件结束-------
                logging.info(u"DubboService.py: execute_testcases: DB请求信息[%s:%s:%s:%s]" % (db_host,db_port,db_user,db_pass))
                db_user = UsualTools.decrypt(db_user)
                db_pass = UsualTools.decrypt(db_pass)
                db = DBTool(db_host,db_port,db_user,db_pass)
                # =================特殊格式化处理变量配置。============================
                varsconf = cp.get_processed_vars(varsconf,env,db)
                logging.debug(u"DubboService.py: execute_testcases: 处理完成的变量配置：%s" % varsconf)
                #================格式化处理变量配置结束==========================

                # =================对data、param、expect等进行变量替换。============================
                #参数处理sqls_string_init、sqls_string_recover、params、expect 的参数 进行参数带入处理
                sqls_string_init = cp.process_vars(sqls_string_init,varsconf,env)
                case_list_with_testresult[i]['data_init'] = sqls_string_init
                sqls_string_recover = cp.process_vars(sqls_string_recover, varsconf, env)
                case_list_with_testresult[i]['data_recover'] = sqls_string_recover
                params = cp.process_vars(params, varsconf, env)
                case_list_with_testresult[i]['params'] = params
                expect = cp.process_vars(expect, varsconf, env)
                case_list_with_testresult[i]['expect'] = expect
                #=====变量替换处理结束============================================================

                # ===数据初始化和数据恢复语句验证Start===
                if sqls_string_init != 'default' :
                    logging.info( UsualTools().get_current_time() + u"DubboService.py: execute_testcases: 进入数据初始化验证。")
                    initTakeTimeStart=time.time()
                    if (cp.validate_sql_strings(sqls_string_init, db) == False):
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 数据初始化验证错误，请检查相应sql语句是否含有where子句或者影响超过%d条数据。" % ServiceConf().sql_effect_lines)
                        continue
                    initTakeTimeEnd=time.time()
                    case_list_with_testresult[i]['initTakeTime'] = initTakeTimeEnd-initTakeTimeStart
                else:
                    logging.info( u"DubboService.py: execute_testcases: 数据初始化默认值default，不进行数据初始化验证。")

                if sqls_string_recover != "default":
                    logging.info( u"DubboService.py: execute_testcases: 进入数据恢复验证。")
                    #db = DBTool(db_host,db_port,db_user,db_pass)
                    if (cp.validate_sql_strings(sqls_string_recover, db) == False):
                        case_list_with_testresult[i]= set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 数据恢复验证错误，请检查相应sql语句是否含有where子句或者影响超过%d条数据。" % ServiceConf().sql_effect_lines)
                        continue
                else:
                    logging.info( u"DubboService.py: execute_testcases: 数据恢复默认值default，不进行数据恢复验证。")
                # =====数据初始化和数据恢复语句验证End=====
                # 数据初始化
                if sqls_string_init != 'default' :
                    logging.info( u"DubboService.py: execute_testcases: 进入数据初始化执行。")
                    #db = DBTool(db_host,db_port,db_user,db_pass)
                    if cp.execute_sql_strings(sqls_string_init, db) == False:
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 数据初始化执行错误，请检查相应sql语句是否正确。".encode('utf8'))
                        case_list_with_testresult[i]['data_init'] = u"[SQL语句有错误，请检查]\r\n" + case_list_with_testresult[i]['data_init']
                        continue
                    is_sqls_string_init_executed = True
                else:
                    logging.info( u"DubboService.py: execute_testcases: 数据初始化默认值default，不进行数据初始化执行。")

                #开始接口调用，校验完成。
                finish = 'dubbo>'  # 命令提示符
                command = 'invoke %s.%s(%s)' % (service_name, method_name, params)
                case_list_with_testresult[i]['host'] = host
                case_list_with_testresult[i]['port'] = port
                case_list_with_testresult[i]['invoke_cmd'] = command
                logging.info( u"DubboService.py: execute_testcases: 执行telnet命令：%s " % command)
                execTakeTimeStart = time.time()
                return_msg = self.do_telnet(host, port, finish, command)
                execTakeTimeEnd = time.time()
                #================处理编码部分=========================
                retMsgEncoding = chardet.detect(return_msg)['encoding'] == None and MyEncode().os_encoding or chardet.detect(return_msg)['encoding'].strip()
                decode_info = MyEncode().os_encoding
                # if retMsgEncoding == "windows-1252":
                #     decode_info = retMsgEncoding
                return_msg = return_msg.decode(decode_info, 'ignore').encode("utf8")  # utf8 return_msg
                return_encode_final = chardet.detect(return_msg)['encoding']
                logging.info( u"DubboService.py: execute_testcases: Invoke后返回消息转换UTF8后编码为%s " % return_encode_final)
                logging.info( u"DubboService.py: execute_testcases: DubboService:执行Invoke后返回实际结果的长度为：%d " % len(return_msg))
                case_list_with_testresult[i]['return_msg'] = return_msg
                is_sqls_string_init_executed = True
                is_get_telnet_return = True
                #得到返回结果，进行断言。分为返回值断言，数据库断言。
                #处理预期结果
                return_expect = cp.get_sub_string(expect, "[RETURN]", "[ENDRETURN]")
                test_result = ""
                assert_msg = ""
                isReturnResultAsserted = False
                if return_expect == False or return_expect.strip()=="":
                    logging.info(u"DubboService.py: execute_testcases: 未发现预期返回值，不进行返回值预期结果断言。 ")
                    isReturnResultAsserted = False
                    test_result = "NO_RESULT"
                else:
                    #进入预期结果断言
                    return_expect_assert_result = cp.assert_result(return_expect,return_msg)
                    logging.info(u"DubboService.py: execute_testcases: 断言结果list:%d" % len(return_expect_assert_result))
                    logging.info(u"DubboService.py: execute_testcases: 断言结果list：%s" % return_expect_assert_result)
                    case_list_with_testresult[i]['perform_time'] = return_expect_assert_result[2]

                    #生成execTakeTime
                    if "ms" in case_list_with_testresult[i]['perform_time'] :
                        tmpTime = case_list_with_testresult[i]['perform_time']
                        case_list_with_testresult[i]['execTakeTime'] = float(tmpTime.replace("ms" , ""))/1000
                    else:
                        case_list_with_testresult[i]['execTakeTime'] = execTakeTimeEnd - execTakeTimeStart

                    test_result = return_expect_assert_result[1] #case_list_with_testresult[i]['test_result']
                    case_list_with_testresult[i]['test_result'] = test_result
                    assert_msg = return_expect_assert_result[0]  #case_list_with_testresult[i]['assert_msg']
                    case_list_with_testresult[i]['assert_msg'] = assert_msg
                    isReturnResultAsserted = True

                dbdata_expect = cp.get_sub_string(expect, "[DBDATA]", "[ENDDBDATA]")
                if dbdata_expect == False or dbdata_expect.strip()=="":
                    logging.info(u"DubboService.py: execute_testcases: 未发现预期数据库数据，不进行数据库预期结果断言。 ")
                    if isReturnResultAsserted == False:
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 用例错误：没有预期结果，也没有数据库预期。无法进行断言。")
                        continue
                elif test_result == "FAIL":
                    logging.info(u"DubboService.py: execute_testcases: 返回结果断言失败，不需要进行数据库断言。 ")
                elif test_result == "ERROR":
                    logging.info(u"DubboService.py: execute_testcases: 返回结果ERROR，不需要进行数据库断言。 ")
                elif test_result == "PASS" or test_result == "NO_RESULT":
                    # 进入数据库结果断言
                    if sqls_string_init=="default": db.flush()
                    assert_db_result = cp.assert_dbdata(dbdata_expect,db)
                    logging.debug(u"DubboService.py: execute_testcases: 数据库断言结果：%s" % assert_db_result)
                    case_list_with_testresult[i]['assert_msg'] = case_list_with_testresult[i]['assert_msg'] + assert_db_result[0].encode("utf8")
                    case_list_with_testresult[i]['test_result'] = assert_db_result[1]
                else:
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 返回结果异常，不是FAIL/PASS/ERROR，请检查用例和测试环境。 ")
                    continue
            except Exception, e:
                case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: %s".encode('utf8') % e)
                continue
            finally:
                # 数据回复
                if sqls_string_recover != 'default' and is_sqls_string_init_executed == True :
                    logging.info( u"DubboService.py: execute_testcases: 进入数据恢复执行。")
                    #db = DBTool(db_host,db_port,db_user,db_pass)
                    recoverTakeTimeStart = time.time()
                    if cp.execute_sql_strings(sqls_string_recover, db) == False:
                        logging.info( u"DubboService.py: execute_testcases: CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。")
                        case_list_with_testresult[i]['data_recover'] = u"[SQL语句有错误，请检查]\r\n" + case_list_with_testresult[i]['data_recover']
                        if is_get_telnet_return == False:
                            case_list_with_testresult[i] =  set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。")

                    recoverTakeTimeEnd = time.time()
                    case_list_with_testresult[i]['recoverTakeTime'] = recoverTakeTimeEnd-recoverTakeTimeStart
                else:
                    logging.info( u"DubboService.py: execute_testcases: 数据恢复默认值default或者未执行数据初始化，不执行数据恢复。")
                    logging.info( u"DubboService.py: execute_testcases: return_msg的值是：%s" % case_list_with_testresult[i]['return_msg'])
                time_end = time.time()
                case_list_with_testresult[i]['totalTakeTime'] = time_end-time_start
                db.release()
                #整体断言结果添加。
                if case_list_with_testresult[i]['test_result'] == "PASS":
                    case_list_with_testresult[i]['assert_msg'] = u"断言结果：PASS。".encode("utf8") + "\n" +case_list_with_testresult[i]['assert_msg']
                elif case_list_with_testresult[i]['test_result'] == "FAIL":
                    case_list_with_testresult[i]['assert_msg'] = u"断言结果：FAIL。".encode("utf8") + "\n" +  case_list_with_testresult[i]['assert_msg']
                elif case_list_with_testresult[i]['test_result'] == "ERROR":
                    case_list_with_testresult[i]['assert_msg'] = u"断言结果：ERROR。".encode("utf8") + "\n" +  case_list_with_testresult[i]['assert_msg']

                logging.info( u"DubboService.py: execute_testcases: 本条用例[%s]执行总时间：%f秒" % (case_id,case_list_with_testresult[i]['totalTakeTime']))
                try:
                    logging.debug(u"case_dict_finally:%s" % case_list_with_testresult[i])
                except Exception,e:
                    logging.debug(u"Finnally error : %s " % e)
                logging.info(u"==================================================================================================================")

        return case_list_with_testresult

    def execute_group_testcases(self, group_case_list=[], config=Config("../ConfFile/test.conf"), env="test"):
        """
        获取excel数据并返回一个list，list包含N个dict，每个dict保存用例Excel中的各个值。规则如下：
        group_case_list[TestcaseGroup对象1，TestcaseGroup对象2]
        :param case_list: 一个列表，列表中每个值都是一个dict，对应的key如下。
                用例编号	名称	描述	系统	服务	方法	数据初始化	数据恢复        参数      预期结果    变量配置    (Excel列名)
                case_id     name    desc    system  service method  data_init   data_recover    params    expect      varsconf    （dict的key）
        :return: case_list_with_testresult: 一个list，主体与case_list一致，只是每个值中的dict增加key returnMsg(执行dubbo接口返回的结果)，对应的key如下。
                用例编号	名称	描述	系统	服务	方法	数据初始化	数据恢复        参数     预期结果    返回结果    (Excel列名)
                case_id     name    desc    system  service method  data_init   data_recover    params   expect      return_msg（dict的key）
        """
        cp = CommonProcess()
        logging.info( u"DubboService.py: execute_testcases: 测试环境是%s" % env)
        group_case_list_with_testresult = group_case_list

        conf = config.conf_dict
        # print conf
        logging.info(u"DubboService.py: execute_testcases: 配置是%s" % conf )

        for tmpj in range(0, len(group_case_list)):
            #获取整个用例组，对当前用例组进行测试，所有步骤通过为PASS，否则以最后一步结果为准。
            logging.info(u"DubboService.py: execute_testcases: 开始执行第%d条用例。" % (tmpj + 1))
            group_case_desc = group_case_list[tmpj].tgcDesc #用例组描述
            # 步骤
            group_case_steps = group_case_list[tmpj].tgcStepList  #用例组步骤列表
            group_time_start = time.time()
            for i in range(0,len(group_case_steps)):
                #获取每一步操作，进行步骤操作，当前步骤如果PASS，继续下一步，如果FAIL或者ERROR，退出循环，后续步骤不在执行，执行下一个用例组。
                time_start = time.time()
                db = DBTool()
                try:
                    case_id = group_case_steps[i].caseId.strip()
                    step = group_case_steps[i].step
                    name = group_case_steps[i].name.strip()
                    desc = group_case_steps[i].desc.strip()
                    sys_name = group_case_steps[i].system.strip()
                    service_name = group_case_steps[i].service.strip()
                    method_name = group_case_steps[i].method.strip()
                    sqls_string_init = group_case_steps[i].data_init.strip().strip()
                    sqls_string_recover = group_case_steps[i].data_recover.strip()
                    params = group_case_steps[i].params.strip()
                    expect = group_case_steps[i].expect.strip()
                    varsconf = group_case_steps[i].varsconf.strip()
                except Exception,e:
                    logging.debug(traceback.format_exc())
                    group_case_steps[i].setError(u"CASE_ERROR: 读取用例数据失败，停止执行本条用例。")
                    break

                try:
                    logging.info(u"DubboService.py: execute_testcases: 开始执行组合用例=>编号[%s]步骤[%s]名称[%s]" % (case_id,step, name))
                    is_sqls_string_init_executed = False
                    is_get_telnet_return = False
                    if case_id == '' or name == '' or desc == '' or sys_name == '' or service_name == '' or method_name == '' or sqls_string_init == '' or sqls_string_recover == '' or expect == '':
                        group_case_steps[i].setError(u"CASE_ERROR: 用例错误，有空字段，请检查用例。")
                        break
                    #用例ID校验TC_sysname_0001
                    case_id_split_list = case_id.split('_')
                    if len(case_id_split_list) == 2 :
                        if case_id_split_list[0] != 'TGC':
                            group_case_steps[i].setError(u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TGC_1 or TC_sysname_1。")
                            break
                        try:
                            if int(case_id_split_list[1]) < 1 :
                                group_case_steps[i].setError(u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TGC_1。")
                                break
                        except Exception, e:
                            group_case_steps[i].setError(u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TGC_1 or TC_sysname_1。")
                            break
                    elif len(case_id_split_list) == 3 :
                        if case_id_split_list[0] != 'TC':
                            group_case_steps[i].setError(u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TGC_1 or TC_sysname_1。")
                            break
                        try:
                            if int(case_id_split_list[2]) < 1 :
                                group_case_steps[i].setError(u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TGC_1。")
                                break
                        except Exception, e:
                            group_case_steps[i].setError(u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TGC_1 or TC_sysname_1。")
                            break
                    #校验step
                    try:
                        if int(step) < 1 :
                            group_case_steps[i].setError(u"CASE_ERROR: 测试步骤不符合规范，应该为大于等于1的整数。")
                            break
                    except Exception, e:
                        group_case_steps[i].setError(u"CASE_ERROR: 测试步骤不符合规范，应该为大于等于1的整数。")
                        break

                    # 校验系统名----解析系统名称------------ 在配置文件中要有
                    if sys_name not in config.sections:
                        group_case_steps[i].setError(
                                                                      u"CASE_ERROR: 测试系统错误：当前系统%s，目前只支持如下系统%s，请检查用例。".encode('utf8') % (sys_name,config.sections))
                        break
                    #校验服务名 com.sdfsdf.sdflasd.sdklf
                    if re.match('^[a-z]+[\.][a-zA-Z0-9.]+[a-zA-Z0-9]$', service_name) == None:
                        group_case_steps[i].setError(
                                                                      u"CASE_ERROR: 用例错误，服务不符合规则，请检查用例。服务应该类似为com.pzj.core.product.service.ScreeingsQueryService")
                        break
                    # 校验接口名字，小写字母开头，只包含字母和数字的驼峰命名法
                    if re.match('^[a-z][0-9a-zA-Z]+$', method_name) == None:
                        group_case_steps[i].setError(
                                                                      u"CASE_ERROR: 用例错误，接口名不符合规则，请检查用例。接口名不符合规则，应该为纯字母数字组合且小写字母开头。如：queryScreeingsById")
                        break

                    #===================加载系统配置信息===============================
                    logging.info( u"DubboService.py: execute_testcases: 所在系统是[%s]" % sys_name)
                    host = conf[sys_name]['host_addr']
                    port = int(conf[sys_name]['host_port'])
                    group_case_steps[i].host = host
                    group_case_steps[i].port = port
                    logging.info( u"DubboService.py: execute_testcases: 请求地址[%s:%d]" % (host, port))
                    db_host = conf[sys_name]['db_host']
                    db_port = int(conf[sys_name]['db_port'])
                    db_user = conf[sys_name]['db_user']
                    db_pass = conf[sys_name]['db_pass']
                    if host == '' or port == '' or db_host == '' or db_port == '' or db_user == '' or db_pass == '':
                        logging.info( u"DubboService.py: execute_testcases: FATAL_ERROR: 配置文件错误！终止执行！请检查配置文件是否包含当前系统的配置。")
                        sys.exit(0)
                    # ----解析系统名称和配置文件结束-------
                    logging.info(u"DubboService.py: execute_testcases: DB请求信息[%s:%s:%s:%s]" % (db_host,db_port,db_user,db_pass))
                    db_user = UsualTools.decrypt(db_user)
                    db_pass = UsualTools.decrypt(db_pass)
                    db = DBTool(db_host,db_port,db_user,db_pass)
                    # =================特殊格式化处理变量配置。============================
                    varsconf = cp.get_processed_vars(varsconf,env,db)
                    logging.debug(u"DubboService.py: execute_testcases: 处理完成的变量配置：%s" % varsconf)
                    #================格式化处理变量配置结束==========================

                    # =================对data、param、expect等进行变量替换。============================
                    #参数处理sqls_string_init、sqls_string_recover、params、expect 的参数 进行参数带入处理
                    sqls_string_init = cp.process_vars(sqls_string_init,varsconf,env)
                    group_case_steps[i].data_init = sqls_string_init
                    sqls_string_recover = cp.process_vars(sqls_string_recover, varsconf, env)
                    group_case_steps[i].data_recover = sqls_string_recover
                    params = cp.process_vars(params, varsconf, env)
                    group_case_steps[i].params = params
                    expect = cp.process_vars(expect, varsconf, env)
                    group_case_steps[i].expect = expect
                    #=====变量替换处理结束============================================================

                    # ===数据初始化和数据恢复语句验证Start===
                    if sqls_string_init != 'default' :
                        logging.info( UsualTools().get_current_time() + u"DubboService.py: execute_testcases: 进入数据初始化验证。")
                        initTakeTimeStart=time.time()
                        if (cp.validate_sql_strings(sqls_string_init, db) == False):
                            group_case_steps[i].setError(u"CASE_ERROR: 数据初始化验证错误，请检查相应sql语句是否含有where子句或者影响超过%d条数据。" % ServiceConf().sql_effect_lines)
                            break
                        initTakeTimeEnd=time.time()
                        group_case_steps[i].initTakeTime = initTakeTimeEnd-initTakeTimeStart

                    else:
                        logging.info( u"DubboService.py: execute_testcases: 数据初始化默认值default，不进行数据初始化验证。")

                    if sqls_string_recover != "default":
                        logging.info( u"DubboService.py: execute_testcases: 进入数据恢复验证。")
                        #db = DBTool(db_host,db_port,db_user,db_pass)
                        if (cp.validate_sql_strings(sqls_string_recover, db) == False):
                            group_case_steps[i].setError(u"CASE_ERROR: 数据恢复验证错误，请检查相应sql语句是否含有where子句或者影响超过%d条数据。" % ServiceConf().sql_effect_lines)
                            break
                    else:
                        logging.info( u"DubboService.py: execute_testcases: 数据恢复默认值default，不进行数据恢复验证。")
                    # =====数据初始化和数据恢复语句验证End=====
                    # 数据初始化
                    if sqls_string_init != 'default' :
                        logging.info( u"DubboService.py: execute_testcases: 进入数据初始化执行。")
                        #db = DBTool(db_host,db_port,db_user,db_pass)
                        if cp.execute_sql_strings(sqls_string_init, db) == False:
                            group_case_steps[i].data_init = u"[SQL语句有错误，请检查]\r\n" + group_case_steps[i].data_init
                            group_case_steps[i].setError(u"CASE_ERROR: 数据初始化执行错误，请检查相应sql语句是否正确。".encode('utf8'))
                            break
                        is_sqls_string_init_executed = True
                    else:
                        logging.info( u"DubboService.py: execute_testcases: 数据初始化默认值default，不进行数据初始化执行。")

                    #开始接口调用，校验完成。
                    finish = 'dubbo>'  # 命令提示符
                    command = 'invoke %s.%s(%s)' % (service_name, method_name, params)
                    group_case_steps[i].host = host
                    group_case_steps[i].port = port
                    group_case_steps[i].invoke_cmd = command
                    logging.info( u"DubboService.py: execute_testcases: 执行telnet命令：%s " % command)
                    execTakeTimeStart = time.time()
                    return_msg = self.do_telnet(host, port, finish, command)
                    execTakeTimeEnd = time.time()
                    #================处理编码部分=========================
                    retMsgEncoding = chardet.detect(return_msg)['encoding'] == None and MyEncode().os_encoding or chardet.detect(return_msg)['encoding'].strip()
                    decode_info = MyEncode().os_encoding
                    # if retMsgEncoding == "windows-1252":
                    #     decode_info = retMsgEncoding
                    return_msg = return_msg.decode(decode_info, 'ignore').encode("utf8")  # utf8 return_msg
                    return_encode_final = chardet.detect(return_msg)['encoding']
                    logging.info( u"DubboService.py: execute_testcases: Invoke后返回消息转换UTF8后编码为%s " % return_encode_final)
                    logging.info( u"DubboService.py: execute_testcases: DubboService:执行Invoke后返回实际结果的长度为：%d " % len(return_msg))
                    group_case_steps[i].return_msg = return_msg
                    is_sqls_string_init_executed = True
                    is_get_telnet_return = True
                    #得到返回结果，进行断言。分为返回值断言，数据库断言。
                    #处理预期结果
                    return_expect = cp.get_sub_string(expect, "[RETURN]", "[ENDRETURN]")
                    test_result = ""
                    assert_msg = ""
                    isReturnResultAsserted = False
                    if return_expect == False or return_expect.strip()=="":
                        logging.info(u"DubboService.py: execute_testcases: 未发现预期返回值，不进行返回值预期结果断言。 ")
                        isReturnResultAsserted = False
                        test_result = "NO_RESULT"
                    else:
                        #进入预期结果断言
                        return_expect_assert_result = cp.assert_result(return_expect,return_msg)
                        logging.info(u"DubboService.py: execute_testcases: 断言结果list:%d" % len(return_expect_assert_result))
                        logging.info(u"DubboService.py: execute_testcases: 断言结果list：%s" % return_expect_assert_result)
                        group_case_steps[i].perform_time = return_expect_assert_result[2]

                        #生成execTakeTime
                        if "ms" in group_case_steps[i].perform_time :
                            tmpTime = group_case_steps[i].perform_time
                            group_case_steps[i].execTakeTime = float(tmpTime.replace("ms" , ""))/1000
                        else:
                            group_case_steps[i].execTakeTime = execTakeTimeEnd - execTakeTimeStart

                        test_result = return_expect_assert_result[1] #case_list_with_testresult[i]['test_result']
                        group_case_steps[i].test_result = test_result
                        assert_msg = return_expect_assert_result[0]  #case_list_with_testresult[i]['assert_msg']
                        group_case_steps[i].assert_msg = assert_msg
                        isReturnResultAsserted = True

                    dbdata_expect = cp.get_sub_string(expect, "[DBDATA]", "[ENDDBDATA]")
                    if dbdata_expect == False or dbdata_expect.strip()=="":
                        logging.info(u"DubboService.py: execute_testcases: 未发现预期数据库数据，不进行数据库预期结果断言。 ")
                        if isReturnResultAsserted == False:
                            group_case_steps[i].setError(u"CASE_ERROR: 用例错误：没有预期结果，也没有数据库预期。无法进行断言。")
                            break
                    elif test_result == "FAIL":
                        logging.info(u"DubboService.py: execute_testcases: 返回结果断言失败，不需要进行数据库断言。 ")
                    elif test_result == "ERROR":
                        logging.info(u"DubboService.py: execute_testcases: 返回结果ERROR，不需要进行数据库断言。 ")
                    elif test_result == "PASS" or test_result == "NO_RESULT":
                        # 进入数据库结果断言
                        if sqls_string_init=="default": db.flush()
                        assert_db_result = cp.assert_dbdata(dbdata_expect,db)
                        logging.debug(u"DubboService.py: execute_testcases: 数据库断言结果：%s" % assert_db_result)
                        group_case_steps[i].assert_msg = group_case_steps[i].assert_msg + assert_db_result[0].encode("utf8")
                        group_case_steps[i].test_result = assert_db_result[1]
                    else:
                        group_case_steps[i].setError(u"CASE_ERROR: 返回结果异常，不是FAIL/PASS/ERROR，请检查用例和测试环境。 ")
                        break
                except Exception, e:
                    group_case_steps[i].setError(u"CASE_ERROR: %s".encode('utf8') % e)
                    break
                finally:
                    #整体断言结果添加。
                    if group_case_steps[i].test_result == "PASS":
                        # group_case_steps[i].assert_msg = u"断言结果：PASS。".encode("utf8") + "\n" + group_case_steps[i].assert_msg
                        t_assert_msg = u"断言结果：PASS。".encode("utf8") + "\n" + group_case_steps[i].assert_msg
                        #TODO 如果当前步骤是最后一步，执行数据回复。
                        if i == len(group_case_steps)-1:
                            #是最后一步，执行数据回复。否则不执行。
                            # 数据回复
                            if sqls_string_recover != 'default' and is_sqls_string_init_executed == True:
                                logging.info(u"DubboService.py: execute_testcases: 进入数据恢复执行。")
                                # db = DBTool(db_host,db_port,db_user,db_pass)
                                recoverTakeTimeStart = time.time()
                                if cp.execute_sql_strings(sqls_string_recover, db) == False:
                                    logging.info(u"DubboService.py: execute_testcases: CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。")
                                    group_case_steps[i].data_recover = u"[SQL语句有错误，请检查]\r\n" + group_case_steps[i].data_recover
                                    if is_get_telnet_return == False:
                                        group_case_steps[i].setError(u"CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。".encode('utf8'))
                                        t_assert_msg = u"断言结果：ERROR。".encode("utf8") + "\n" + group_case_steps[i].assert_msg
                                recoverTakeTimeEnd = time.time()
                                group_case_steps[i].recoverTakeTime = recoverTakeTimeEnd - recoverTakeTimeStart
                            else:
                                logging.info(u"DubboService.py: execute_testcases: 数据恢复默认值default或者未执行数据初始化，不执行数据恢复。")
                                logging.info(u"DubboService.py: execute_testcases: return_msg的值是：%s" % group_case_steps[i].return_msg)

                        time_end = time.time()
                        group_case_steps[i].assert_msg = t_assert_msg
                        group_case_steps[i].totalTakeTime = time_end - time_start
                        db.release()
                    elif group_case_steps[i].test_result == "FAIL":
                        t_assert_msg = u"断言结果：FAIL。".encode("utf8") + "\n" +  group_case_steps[i].assert_msg
                        #执行数据回复并退出循环，不再执行后续步骤。
                        # 数据回复
                        if sqls_string_recover != 'default' and is_sqls_string_init_executed == True:
                            logging.info(u"DubboService.py: execute_testcases: 进入数据恢复执行。")
                            # db = DBTool(db_host,db_port,db_user,db_pass)
                            recoverTakeTimeStart = time.time()
                            if cp.execute_sql_strings(sqls_string_recover, db) == False:
                                logging.info(u"DubboService.py: execute_testcases: CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。")
                                group_case_steps[i].data_recover = u"[SQL语句有错误，请检查]\r\n" + group_case_steps[i].data_recover
                                if is_get_telnet_return == False:
                                    group_case_steps[i].setError(
                                                                        u"CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。".encode(
                                                                            'utf8'))
                                    t_assert_msg = u"断言结果：ERROR。".encode("utf8") + "\n" + group_case_steps[i].assert_msg
                            recoverTakeTimeEnd = time.time()
                            group_case_steps[i].recoverTakeTime = recoverTakeTimeEnd - recoverTakeTimeStart
                        else:
                            logging.info(u"DubboService.py: execute_testcases: 数据恢复默认值default或者未执行数据初始化，不执行数据恢复。")
                            logging.info(
                                u"DubboService.py: execute_testcases: return_msg的值是：%s" % group_case_steps[i].return_msg)

                        time_end = time.time()
                        group_case_steps[i].assert_msg = t_assert_msg
                        group_case_steps[i].totalTakeTime = time_end - time_start
                        db.release()
                        break
                    elif group_case_steps[i].test_result == "ERROR":
                        t_assert_msg = u"断言结果：ERROR。".encode("utf8") + "\n" +  group_case_steps[i].assert_msg
                        #执行数据回复并退出循环，不再执行后续步骤。
                        # 数据回复
                        if sqls_string_recover != 'default' and is_sqls_string_init_executed == True:
                            logging.info(u"DubboService.py: execute_testcases: 进入数据恢复执行。")
                            # db = DBTool(db_host,db_port,db_user,db_pass)
                            recoverTakeTimeStart = time.time()
                            if cp.execute_sql_strings(sqls_string_recover, db) == False:
                                logging.info(u"DubboService.py: execute_testcases: CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。")
                                group_case_steps[i].data_recover = u"[SQL语句有错误，请检查]\r\n" + group_case_steps[i].data_recover
                                if is_get_telnet_return == False:
                                    group_case_steps[i].setError(
                                                                        u"CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。".encode(
                                                                            'utf8'))
                                    t_assert_msg = u"断言结果：ERROR。".encode("utf8") + "\n" + group_case_steps[i].assert_msg
                            recoverTakeTimeEnd = time.time()
                            group_case_steps[i].recoverTakeTime = recoverTakeTimeEnd - recoverTakeTimeStart
                        else:
                            logging.info(u"DubboService.py: execute_testcases: 数据恢复默认值default或者未执行数据初始化，不执行数据恢复。")
                            logging.info(
                                u"DubboService.py: execute_testcases: return_msg的值是：%s" % group_case_steps[i].return_msg)

                        time_end = time.time()
                        group_case_steps[i].assert_msg = t_assert_msg
                        group_case_steps[i].totalTakeTime = time_end - time_start
                        db.release()
                        break

                    logging.info( u"DubboService.py: execute_testcases: 本条用例[%s]执行总时间：%f秒" % (case_id,group_case_steps[i].totalTakeTime))
                    try:
                        logging.debug(u"case_dict_finally:%s" % group_case_steps[i].toString())
                    except Exception,e:
                        logging.debug(u"Finnally error : %s " % e)
                    logging.info(u"==================================================================================================================")

            group_time_end = time.time()
            #此处处理desc部分，step部分已经处理完毕 根据group_case_steps的各步骤结果进行用例组group_case_desc最终断言
            tmp_test_result = "ERROR"
            tmp_assert_msg = "ERROR：用例执行异常，没有返回结果！"
            passcount = 0
            for i in range(0,len(group_case_steps)):
                if group_case_steps[i].test_result == "PASS":
                    passcount += 1
                elif group_case_steps[i].test_result == "FAIL" or group_case_steps[i].test_result == "ERROR":
                    tmp_test_result = group_case_steps[i].test_result
                    tmp_assert_msg = group_case_steps[i].assert_msg
                    break
            if passcount == len(group_case_steps):
                tmp_test_result = "PASS"
                tmp_assert_msg = u"PASS：所有步骤测试通过。"

            #赋值给group_case_desc
            group_case_desc.test_result = tmp_test_result
            group_case_desc.assert_msg = tmp_assert_msg
            #将group_case_desc group_case_steps赋值给group_case_list_with_testresult对应的位置
            group_case_list_with_testresult[tmpj].tgcStepList = group_case_steps
            group_case_list_with_testresult[tmpj].tgcDescDict = group_case_desc

        #log打印最终结果
        for tmpgli in range(0,len(group_case_list_with_testresult)):
            logging.debug(u"VALUE%d:%s" % (tmpgli,group_case_list_with_testresult[tmpgli].toStringList()))

        return group_case_list_with_testresult

    def do_telnet(self, host, port, finish, command):
        """执行telnet命令
        :param host:
        :param port:
        :param finish:
        :param command:
        :return:
        """
        import telnetlib
        # 连接Telnet服务器
        try:
            tn=""
            logging.debug(u'DubboService.py: do_telnet: command：%s ' % command)
            # logging.debug(u'DubboService.py: do_telnet: command编码：%s ' % chardet.detect(command)['encoding'])
            is_conn_telnet = False
            logging.debug(u'DubboService.py: do_telnet: telent init')
            tn = telnetlib.Telnet(host, port, timeout=10)
            logging.debug(u'DubboService.py: do_telnet:telent connected')
            tn.set_debuglevel(0)  # 设置debug输出级别  0位不输出，越高输出越多
            logging.debug(u'DubboService.py: do_telnet:telent set debug level')
            # 输入回车
            tn.write('\n')
            logging.debug(u'DubboService.py: do_telnet:telent enter')
            # 执行命令
            none_until = tn.read_until(finish)
            logging.debug(u'DubboService.py: do_telnet: telent enter return: %s' % none_until)
            if none_until.strip() == finish :
                is_conn_telnet = True
            tn.write('%s\r\n' % command.decode("utf8").encode(MyEncode().os_encoding))
            logging.debug(u'DubboService.py: do_telnet:telent enter command: %s ' % command)
            # 执行完毕后，终止Telnet连接（或输入exit退出）
            return_msg =  tn.read_until(finish)
            logging.debug(u'DubboService.py: do_telnet: telent enter command after read_until')
            logging.debug(u'DubboService.py: do_telnet: return_msg：%d ' % len(return_msg))
            logging.debug(u'DubboService.py: do_telnet: return_msg encoding：%s ' % chardet.detect(return_msg)['encoding'])
            return return_msg
        except Exception, e:
            if is_conn_telnet:
                logging.info(u"DubboService.py: do_telnet: 请求参数错误等异常，导致请求返回异常。")
                return u"请求参数错误等异常，导致请求返回异常。".encode(MyEncode().os_encoding)
            else:
                logging.info( u"DubboService.py: do_telnet: Telnet请求时发生网络问题或者接口错误，请确认。")
                return u"TELNET_ERROR: Telnet请求时发生网络问题或者接口错误，请确认。".encode(MyEncode().os_encoding)
        finally:
            if type(tn) != type(""): tn.close()


