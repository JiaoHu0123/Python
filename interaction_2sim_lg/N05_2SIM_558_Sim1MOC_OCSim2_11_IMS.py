#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-25

@author: molly
ScriptName:SLAB_N05_Interaction_2SIM_558_Sim1 MOC and OpenCloseSim2_11_IMS.py
Function:  MainCard:SIM2&DataCard:SIM2
           Sim1 MOC and OpenCloseSim2(IMS)
'''
import android
import ConfigParser  # get config file data
import os, sys  # use for path
import time  # use for time
import re  # rename slog name

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
testTimes = config.get("Setting", "Nw")  # get test times
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
droid.log("parent path=" + BASE_DIR)
droid.log("parent_dir=" + Par_DIR)
droid.log("hold time=" + hold_time)

    
#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "LTE", "L+G", "SingleVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "IMS", "LTE", simtype, "Card Switch", "L+G", "120", SIM1Status, SIM2Status, Network1Status, Network2Status)

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
if "LTE" in defaultMode:
    supportLTE = True
elif "AUTO" in defaultMode:
    droid.log("AUTO MODE")
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))

# check whether supported volte
if nwObject.checkVolte(droid, sim):
    supportVolte = True
else:
    supportVolte = False
    droid.log("summary:NOT_SUPPORT") 
    exit() 
droid.log("supportVolte=" + str(supportVolte))
#============================================================================================================
def CloseSim(sim):
    if nwObject.closeSim(droid, sim):
        passFlag = True
    else:
        passFlag = False
    return passFlag 
def OpenSim(sim):
    if nwObject.openSim(droid, sim):
        passFlag1 = True
    else:
        passFlag1 = False
    return passFlag1

# close sim1 ,sim2 moc,open sim1
def OpenCloseSIM_MOC(droid, callNumber, hold_time):
    global passTimes, failTimes
    callObject.setPreCondition(droid, 1, 1)
    for i in range(1, int(testTimes) + 1):
        droid.log("This is the " + str(i) + " times test:")
        droid.log("==================step1:  close sim" + str(2) + ",and wait 5s")
        time.sleep(5)
        closeFlag = CloseSim(1)
        mocFlag = callObject.voiceCall(droid, callNumber, hold_time)
        time.sleep(20)
        openFlag = OpenSim(1)
        droid.log("===CloseSim(2)=" + str(closeFlag) + "===OpenSim(2)=" + str(openFlag) + "===moc(1)=" + str(mocFlag))
        if closeFlag & mocFlag & openFlag :
            passTimes += 1
        else:
            failTimes += 1
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))  
    callObject.setPreCondition(droid, 0, 0)
    

#============================================================================================================
droid.sendCommand("IsPluginSimCard 0", "OK")
droid.sendCommand("IsPluginSimCard 1", "OK")
sim = callObject.getMainCard(droid)
net = nwObject.getNetClass(droid, sim)
volteFlag = nwObject.checkVolte(droid, sim)
simtype = callObject.getSimType(droid, sim)
callNumber = callObject.getCardType(droid, 0)
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
    droid.log("************************************pluginSim two card=================================") 
    if net == "4G" and volteFlag:
        OpenCloseSIM_MOC(droid, callNumber, hold_time)
    elif supportLTE:
        nwObject.startSearchNet(droid, sim)
        nwObject.selLTE(droid, simtype) 
        OpenCloseSIM_MOC(droid, callNumber, hold_time) 
    else:
        exit()    
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    cardtype = "SINGLE1"
    droid.log("only sim1")
    droid.log("summary:NOT_SUPPORT")
    exit()
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "SINGLE2"
    droid.log("only sim2")
    droid.log("summary:NOT_SUPPORT") 
    exit()
else:
    # update:panbing
    droid.log("just plugin one simCard or no simCard")
    network = "NO_NET" 
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT")
    exit()
                
commObject.result(droid,testTimes, passTimes, failTimes)
