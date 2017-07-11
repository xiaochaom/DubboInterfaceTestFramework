# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

class PromptMsg(object):
    #runPlatformTask.py
    otherException = u"其他异常，异常信息："
    protocolError = u"协议错误，当前仅支持DUBBO和HTTP协议，当前协议："
    loadConfig = u"加载配置"
    loadLogPath = u"加载log输出路径"
    paramMsg = u"参数构建完成，参数为"
    startTask = u"开始执行任务："
    startDubboTask = u"开始执行DUBBO任务。"
    finishDubboTaskReturn = u"DUBBO任务执行成功，返回值为"
    finishDubboTask = u"DUBBO任务执行完成。"

    startHttpTask = u"开始执行HTTP任务。"
    finishHttpTaskReturn = u"HTTP任务执行成功，返回值为"
    finishHttpTask = u"HTTP任务执行完成。"

    #runCaseDebugTask.py
    startDebugTask = u"开始执行DUBBO调试任务"
    execSuccess = u"执行成功！"
    intoDbSuccess = u"写入数据库成功！"
    debugFailMsg = u"调试失败，未返回实际结果，请检查用例。"
    exceptionAndCheck = u"发生异常，未返回实际结果，请检查用例。"

    startHttpDebugTask = u"开始执行HTTP调试任务"

    #runWebPlatformFunc.py
    funcTakeTime = u"函数占用时间"
    noneCaseFail = u"用例列表为空，执行失败！"
    reportFailAndReason = u"测试报告生成失败,原因："
    emailNotSend = u"EMAIL_NOT_SEND"

    #runTaskCancel.py
    taskCanceled = u"任务已取消。任务ID："
