#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-7-7

@author: jingjing.nan
ScriptName:
Function:  sim2 is main card and data card,close sim2 volte,sim1 sms,open sim1
'''
import android
import ConfigParser  # get config file data
import os, sys  # use for path
import time  # use for time
#import re  # rename slog name

# define vars
caseTimeOut = 200
config = ConfigParser.ConfigParser()
BASE_DIR = os.path.dirname(__file__)  # test scripts path name   #get parent path 
parent_dir = os.path.split(BASE_DIR)
Par_DIR = parent_dir[0]
Setting_path = os.path.join(Par_DIR, 'Settings.ini')
config.readfp(open(Setting_path, 'r'))
droid = android.Android(scriptname=__file__)
basic_path = os.path.abspath(Par_DIR)
droid.log(basic_path)
sys.path.append(basic_path)

version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname

import basic.importMethod
basic.importMethod.importMethod()

from basic import common
from basic import call
from basic import net
from basic import sms
droid.setCaseTimeOut(caseTimeOut)

passTimes = 0
failTimes = 0
phoneId = 1  # 0-sim1;1-sim2
global testTimes
testTimes = config.get("Setting", "interaction")  # get test times
hold_time = config.get("Setting", "callHoldTime")
droid.log("The test times is " + testTimes)
nwObject = net.NetWork(scriptname = __file__)
commObject = common.Common(scriptname = __file__)
callObject=call.MMC(scriptname = __file__) 
smsObject = sms.SMS(scriptname = __file__)
print droid.log("parent path=" + BASE_DIR)
print droid.log("parent_dir=" + Par_DIR)
print droid.log(" =============================signal sim,open close sim card==========================")
global simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)

#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "MULTI", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "INTERACTION", "MULTI", simtype, "SMS", "L+G", "30", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================

sim = callObject.getMainCard(droid)
flagVolte = nwObject.checkVolte(droid, sim)
if flagVolte:
    droid.log("supportVolte")
else:
    droid.log("NotSupportVolte,the case will exit") 

defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
# check whether supported LTE
if "LTE" or "AUTO" in defaultMode:
    supportLTE = True
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))
if supportLTE:
    droid.log("supported LTE")
else:
    droid.log("don't supported Volte")
    droid.log("summary:NOT_SUPPORT")
    exit()
#=================================================================================================   
def SMS():
    flagSetSMSCard = smsObject.setSMSSim(droid, 0)
    time.sleep(20)
    Sms_Num = smsObject.getSmsNumber(droid, 0)
    droid.log(Sms_Num)
    Content = smsObject.getContent()
    flagSendSms = smsObject.sendSMS(droid, Sms_Num, Content)
    time.sleep(10)
    if flagSetSMSCard and flagSendSms:
        passflag = True
        droid.log("SMS pass")
    else:
        passflag = False 
        droid.log("sms===fail")
    return passflag
    
def CloseVolte(sim):
    if nwObject.closeVOLTE(droid, sim):
        passFlag = True
    else:
        passFlag = False
    return passFlag 
def OpenVolte(sim):
    if nwObject.openVOLTE(droid, sim):
        droid.log("====================step2: open card,and wait 30s")
        passFlag1 = True
    else:
        passFlag1 = False
    return passFlag1
# close sim1 ,sim2 sms,open sim1
def OCV_SMS():
    global passTimes, failTimes
    callObject.setMainCard(droid, 1)
    callObject.setDataCard(droid, 1)
    time.sleep(30)
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test beagin :")
        # check net
        simType1 = callObject.getSimType(droid, 0)
        simType2 = callObject.getSimType(droid, 1)
        droid.log("sim1Type =" + simType1 + "sim2Type=" + simType2)
        net1 = nwObject.getNetClass(droid, 0)
        net2 = nwObject.getNetClass(droid, 1)
        droid.log("sim1 network=" + net1 + "sim2 network=" + net2)
        if net2 == "4G":
            passFlag1 = CloseVolte(1)
            passFlag = SMS()
            time.sleep(20)
            passFlag2 = OpenVolte(1)
            passFlag = SMS()
            time.sleep(20)
            if passFlag & passFlag1 & passFlag2:
                passTimes += 1
            else:
                failTimes += 1
        else:
            droid.log("no 4G net")
    droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))  
    callObject.setPreCondition(droid, 0, 0)
    time.sleep(30)
    
#============================================================================================================
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    print droid.log("************************************pluginSim two card=================================")
    droid.log("pluginSim two card")
    sim = callObject.getMainCard(droid)
    cardtype = "DUAL"
    network = nwObject.getNetSate(droid, sim)
    simtype = callObject.getSimType(droid, sim)
    OCV_SMS()
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    droid.log("summary:NOT_SUPPORT")
    cardtype = "SINGLE1"
    sim = callObject.getMainCard(droid)
    network = nwObject.getNetSate(droid, sim)
    simtype = callObject.getSimType(droid, int(sim))
    exit()
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("summary:NOT_SUPPORT")
    cardtype = "SINGLE2"
    sim = callObject.getMainCard(droid)
    network = nwObject.getNetSate(droid, sim)
    simtype = callObject.getSimType(droid, int(sim))    
    exit()
else:
    droid.log("summary:NOT_SUPPORT")
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    exit()
commObject.result(droid,testTimes, passTimes, failTimes)
