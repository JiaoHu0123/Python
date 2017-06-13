#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-6-3
@author: panbin.ai
CaseName: 
    SLAB_N05_Interaction_2SIM_258_EMC_OpenCloseLTE
Fuction: 
    SIM2 MAIN CARD,SIM0 DATA CARD
    EMC & OpenCloseLTE
'''
import android
import ConfigParser  # get config file data
import os, sys, time  # use for path
# define vars
# import the basic 
droid = android.Android(scriptname=__file__)
droid.log("import basic file")
config = ConfigParser.ConfigParser()
BASE_DIR = os.path.dirname(__file__)  # test scripts path name   #get parent path 
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
droid.log("import the call")
from basic import call  
droid.log("import the common")
from basic import common
from basic import net
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
global simtype, cardtype
testTimes = config.get("Setting", "emcTimes")  # get test times
droid.log("The test times is " + testTimes)
nwObject = net.NetWork(scriptname=__file__)
commObject = common.Common(scriptname=__file__)
callObject = call.MMC(scriptname=__file__) 
hold_time = config.get("Setting", "callHoldTime")
emcNum = config.get("CallNum", "emc")
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname

global simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)
netWork = nwObject.getNetClass(droid, sim)
    
#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "LTE", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "INTERACTION", "LTE", simtype, "Emergency Call", "L+G", "20", SIM1Status, SIM2Status, Network1Status, Network2Status)

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
#===================================================
def EMC_OpenCloseLTE():
    global passTimes
    global failTimes
    flag = False
    if callObject.emcCall(droid, emcNum, hold_time):
        if nwObject.closeVOLTE(droid, 1):
            droid.log("close VOLTE====pass")
            time.sleep(10)
            if nwObject.openVOLTE(droid, 1):
                droid.log("open VOLTE====pass")
                flag = True
        callObject.endCall(droid)
    else:
        droid.log("EMC Call===fail")  
        flag = False  
    return flag
#===================================================
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
    if callObject.setMainCard(droid, 1):
        callObject.setDataCard(droid, 0)
        time.sleep(40)
        for i in range(1, int(testTimes) + 1):
            simType1 = callObject.getSimType(droid, 0)
            simType2 = callObject.getSimType(droid, 1)
            droid.log("sim1Type =" + simType1 + "sim2Type=" + simType2)
            net1 = nwObject.getNetClass(droid, 0)
            net2 = net = nwObject.getNetClass(droid, 1)
            droid.log("sim1 network=" + net1 + "sim2 network=" + net2)
            droid.log("The " + str(i) + " times test begin :")
            if EMC_OpenCloseLTE():
                passTimes += 1
            else:
                failTimes += 1
        callObject.setMainCard(droid, 0)
        callObject.setDataCard(droid, 0)
        time.sleep(30) 
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   
    # update:panbing
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    droid.log("summary:NOT_SUPPORT")
    droid.log("only one sim card1")
    cardtype = "SINGLE1"
    netWork = nwObject.getNetClass(droid, 0)
    simtype = callObject.getSimType(droid, 0)
    droid.log("summary:NOT_SUPPORT")
    exit()
                
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("summary:NOT_SUPPORT")
    droid.log("only one sim card2")
    cardtype = "SINGLE2"
    netWork = nwObject.getNetClass(droid, 1)
    simtype = callObject.getSimType(droid, 1)
    droid.log("summary:NOT_SUPPORT")
    exit()
                
else:
    droid.log("summary:NOT_SUPPORT")
    droid.log("no sim card")
    netWork = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT")
    exit()
                
droid.log("=============THIS CASE TEST END==============")
commObject.result(droid,testTimes, passTimes, failTimes)
