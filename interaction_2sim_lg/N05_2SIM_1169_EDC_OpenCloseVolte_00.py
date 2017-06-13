#!/user/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-20

@author: jingjing.nan
CaseName:SLAB_N05_Interaction_2SIM_1169_ExchangeDataCard_OpenCloseVolte_00
Function:
    sim1 main card, data card. sim1 exchangeDataCard and OpenCloseVolte
   
'''

import android
import ConfigParser
import os, sys

caseTimeOut = 200
config = ConfigParser.ConfigParser()
droid = android.Android(scriptname=__file__)
BASE_DIR = os.path.dirname(__file__)
parent_dir = os.path.split(BASE_DIR)
Par_DIR = parent_dir[0]
Setting_path = os.path.join(Par_DIR, 'Settings.ini')
config.readfp(open(Setting_path, 'r'))
basic_path = os.path.abspath(Par_DIR)
droid.log(basic_path)
sys.path.append(basic_path)
droid.log("import the method")

import basic.importMethod
basic.importMethod.importMethod()
from basic import call
from basic import common
from basic import net
import time
droid.log("import file finish")
time.sleep(10)
droid.setCaseTimeOut(caseTimeOut)
#===========================================================================================
passTimes = 0
failTimes = 0
phoneId = 1  # 0-sim1;1-sim2
global testTimes
global network, simtype, cardtype
testTimes = config.get("Setting", "interaction")
hold_time = config.get("Setting", "callHoldTime")

droid.log("the test times is" + testTimes)
defaultMode = droid.getCommandReturn("GetNetworkMode")
callObject=call.MMC(scriptname = __file__) 
commObject = common.Common(scriptname = __file__)
nwObject = net.NetWork(scriptname = __file__)
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname;
droid.log("The test times is " + testTimes)
webSite = config.get("BrowserAdd", "wapAddress") 
defaultModeInt = nwObject.getModeStrToInt(defaultMode)
droid.log("the default mode int is " + str(defaultModeInt))

sim = callObject.getMainCard(droid)
cardtype = "DUAL"
network = nwObject.getNetSate(droid, sim)
simtype = callObject.getSimType(droid, sim)

#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "MULTI", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "INTERACTION", "MULTI", simtype, "VoLTE Swith", "L+G", "120", SIM1Status, SIM2Status, Network1Status, Network2Status)

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
if "LTE" or "AUTO" in defaultMode:
    supportLTE = True
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))
if supportLTE:
    droid.log("supported LTE")
else:
    droid.log("don't supported LTE")
    droid.log("summary:NOT_SUPPORT") 
    exit()
#===========================================================================================
def CloseVolte(sim):
    if nwObject.closeVOLTE(droid, sim):
        passFlag = True
    else:
        passFlag = False
    return passFlag 
def OpenVolte(sim):
    if nwObject.openVOLTE(droid, sim):
        passFlag1 = True
    else:
        passFlag1 = False
    return passFlag1
def MDC_OCL(droid, testTimes, hold_time):
    global passTimes
    global failTimes
    DataCard = callObject.setDataCard(droid, 1)
    time.sleep(10)
    closeVolte = CloseVolte(0)
    time.sleep(40)
    openVolte = OpenVolte(0)
    time.sleep(40)
    if DataCard and closeVolte & openVolte:
        flag = True
    else:
        flag = False
    return flag
    callObject.setPreCondition(droid, 0, 0)
    time.sleep(30)    
#===========================================================================================  
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("************************************pluginSim two card=================================")
    droid.log("pluginSim two card")
    cardtype = "DUAL"
    callObject.setMainCard(droid, 0)
    callObject.setDataCard(droid, 0)
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
        if MDC_OCL(droid, testTimes, hold_time):
            passTimes += 1
        else:
            failTimes += 1
    droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))
    callObject.setPreCondition(droid, 0, 0)
    time.sleep(30) 
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    cardtype = "SINGLE1"
    droid.log("summary:NOT_SUPPORT") 
    exit()
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "SINGLE2"
    droid.log("summary:NOT_SUPPORT") 
    exit()
else:
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT") 
    exit()
commObject.result(droid,testTimes, passTimes, failTimes)
