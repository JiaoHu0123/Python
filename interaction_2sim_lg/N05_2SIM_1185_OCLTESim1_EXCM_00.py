#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-23

@author: jingjing.nan
ScriptName:SLAB_N05_Interaction_2SIM_1185_OpenCloseLTESim1_ExchangeMainCard_00
Function:  sim1 maincard and datacard
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
import basic.importMethod
basic.importMethod.importMethod()

from basic import common
from basic import net
from basic import call
from basic import sms
droid.setCaseTimeOut(caseTimeOut)

passTimes = 0
failTimes = 0
phoneId = 1  # 0-sim1;1-sim2
testTimes = config.get("Setting", "interaction")  # get test times
hold_time = config.get("Setting", "callHoldTime")
emcNum = config.get("CallNum", "emc")

droid.log("The test times is " + testTimes)
nwObject = net.NetWork(scriptname = __file__)
commObject = common.Common(scriptname = __file__)
callObject=call.MMC(scriptname = __file__) 
smsObject = sms.SMS(scriptname = __file__) 
print droid.log("parent path=" + BASE_DIR)
print droid.log("parent_dir=" + Par_DIR)
print droid.log(" =============================signal sim,open close sim card==========================")

sim = callObject.getMainCard(droid)
network = nwObject.getNetClass(droid, sim)
simtype = callObject.getSimType(droid, sim)
cardtype = "DUAL"
droid.log("===sim=" + sim + "===network=" + network + "===simtype=" + simtype)
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname

#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "MULTI", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "INTERACTION", "MULTI", simtype, "4G Swith", "L+G", "120", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================

defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
#===============================================================================================
def CloseLte(sim):
    if nwObject.closeLte(droid):
        time.sleep(10)
        passFlag = True
    else:
        passFlag = False
    return passFlag 
def OpenLte(sim):
    if nwObject.openLte(droid):
        droid.log("====================step2: open card,and wait 30s")
        time.sleep(30)
        passFlag1 = True
    else:
        passFlag1 = False
    return passFlag1
def OpenCloseLTE_EMC():
    global passTimes, failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("This is the " + str(i) + " times test:")
        callObject.setPreCondition(droid, 0, 0)
        droid.log("==================step1:  close sim" + str(0) + ",and wait 5s")
        time.sleep(5)
        closeLte = CloseLte(0)
        time.sleep(30)
        openLte = OpenLte(0)
        time.sleep(30)
        mainCrad = callObject.setMainCard(droid, 1)
        time.sleep(30)
        if closeLte & openLte & mainCrad:
            passTimes += 1
        else:
            failTimes += 1
    droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))  
    callObject.setPreCondition(droid, 0, 0)
    time.sleep(30)
    
#============================================================================================================
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
    droid.log("************************************pluginSim two card=================================") 
    OpenCloseLTE_EMC()
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    cardtype = "SINGLE1"
    droid.log("summary:NOT_SUPPORT")
    exit()
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "SINGLE2"
    droid.log("summary:NOT_SUPPORT") 
    exit()
else:
    droid.log("just plugin one simCard or no simCard")
    network = "NO_NET" 
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT") 
    exit()
commObject.result(droid,testTimes, passTimes, failTimes)
