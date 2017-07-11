# -*- coding: utf-8 -*-
import sys,re,time,types
sys.path.append("..")
import requests # python处理http相关的类库

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..")

import json,logging

from TestcaseHttpDesc import TestcaseHttpDesc
from TestcaseHttpStep import TestcaseHttpStep

from Config.Const import *

u'''
描述：用例组对象，包含用例描述对象，用例步骤对象列表
作者：王吉亮
日期：2017年6月20日
'''
class TestcaseHttpGroup(object):

    def __init__(self,tgcDesc = TestcaseHttpDesc(),tgcStepList = [], tgcType = TESTCASE_TYPE_GROUP):
        self.tgcDesc = tgcDesc   #详情字典{'title':'测试交易支付流程','desc':'这个是测试交易支付流程的用例组合，有N步测试。','tgcId':'TGC_1'}
        self.tgcStepList = tgcStepList  #步骤列表 [TestcaseStep对象1,TestcaseStep对象2]
        self.tgcType = tgcType  #group 或者 interface  组合用例或者接口用例

    def copy(self,newGroupCase):
        self.tgcDesc = newGroupCase.tgcDesc   #详情字典{'title':'测试交易支付流程','desc':'这个是测试交易支付流程的用例组合，有N步测试。','tgcId':'TGC_1'}
        self.tgcStepList = newGroupCase.tgcStepList  #步骤列表 [TestcaseStep对象1,TestcaseStep对象2]
        self.tgcType = newGroupCase.tgcType  #group 或者 interface  组合用例或者接口用例

    def addStep(self,tgcStep = TestcaseHttpStep()):
        self.tgcStepList.append(tgcStep)

    def detStepByStepId(self,stepId):
        for i in range(0,len(self.tgcStepList)):
            if self.tgcStepList[i].step == stepId:
                self.tgcStepList.remove(i)

    def validateSteps(self):
        stepsIdList = []
        for tmpStep in self.tgcStepList:
            stepsIdList.append(tmpStep.stepId)
        newStepIdList = list(set(stepsIdList)) #对生成的list去重
        if len(newStepIdList) == len(stepsIdList):
            for i in range(0,len(stepsIdList)):
                if i != int(stepsIdList[i]) - 1:
                    return False
            return True
        else:
            return False

    def sortSteps(self):
        stepsIdList = []
        for tmpStep in self.tgcStepList:
            stepsIdList.append(tmpStep.stepId)
        stepsIdList.sort()
        sortedTgcStepList = []
        for tmpStepId in stepsIdList:
            for i in range(0,len(self.tgcStepList)):
                if self.tgcStepList[i].stepId == tmpStepId:
                    sortedTgcStepList.append(self.tgcStepList[i])

        self.tgcStepList = sortedTgcStepList
        return

    def toStringList(self):
        retList = []
        retList.append(self.tgcDesc.toString())
        retList.append([])
        for tmpi in range(0,len(self.tgcStepList)):
            retList[1].append(self.tgcStepList[tmpi].toString())
        return retList
