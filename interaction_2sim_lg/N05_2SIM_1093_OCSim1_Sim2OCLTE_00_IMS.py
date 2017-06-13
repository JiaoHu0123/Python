#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2016-8-25

@author: PANPAN.WEI
ScriptName:SLAB_N05_Interaction_2SIM_1093_OpenCloseSim2_Sim1OpenCloseLTE_00_IMS.py
Function: 1. Close Maincard Sim2,then maincard change to Sim1
2. OpenSim2,wait 30s, Sim1 Modechange
3. Set to default settings
4. loop step1-3
'''
import android
import ConfigParser  # get config file data
import os, sys  # use for pathS
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
#import basic.importMethod
defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
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
defaultModeInt = nwObject.getModeStrToInt(defaultMode)
droid.log("the default mode int is " + str(defaultModeInt))
sim = callObject.getMainCard(droid)
network = nwObject.getNetClass(droid, sim)
simtype = callObject.getSimType(droid, sim)
cardtype = "DUAL"
droid.log("===sim=" + sim + "===network=" + network + "===simtype=" + simtype)
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname

#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "MULTI", "L+G", "SingleVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "IMS", "MULTI", simtype, "Card Switch", "L+G", "120", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================
    
if "LTE" in defaultMode:
    supportLTE = True
elif "AUTO" in defaultMode:
    droid.log("AUTO MODE")
    supportLTE = True
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))

volteFlag = nwObject.checkVolte(droid, sim)

if network == "4G" and volteFlag:
        droid.log("--------4g_ims--------------")
        netvolte = True
        
elif supportLTE:
        nwObject.startSearchNet(droid, sim)
        nwObject.selLTE(droid, simtype) 
        volteFlag = nwObject.checkVolte(droid, sim)
        droid.log("--------4g_ims--------------")
        netvolte = True 
else:
        netvolte = False
        droid.log("------no_ims--------------")
#====================================================================================    
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

# close sim1 ,sim2 sms,open sim1

def OpenCloseSim1_OpenCloseSim2():
    global passTimes, failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("This is the " + str(i) + " times test:")
        callObject.setMainCard(droid, 0)
        time.sleep(30)
        callObject.setDataCard(droid, 0)
        time.sleep(20)
#         droid.log("==================step1:  close sim"+str(0)+",and wait 10s")
        passFlag = CloseSim(0)
        time.sleep(30)    
        passFlag1 = CloseLte(1)
        time.sleep(30)
        passFlag2 = OpenLte(1)                                                              
        time.sleep(30)
        passFlag3 = OpenSim(0)                                                              
        time.sleep(30)
        if passFlag & passFlag1 & passFlag2 & passFlag3:
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
        sim1type = callObject.getSimType(droid, 0)
        net1 = nwObject.getNetClass(droid, 0)
        sim2type = callObject.getSimType(droid, 1)
        net2 = nwObject.getNetClass(droid, 1)
        droid.log("sim1 simtype=" + sim1type + "sim2 simtype=" + sim2type)
        droid.log("sim1 net=" + net1 + "sim2 net=" + net2)
        if net1 == "UNKNOW":
            droid.log("main card sim1 no service, wait 20s,check again")
            time.sleep(20)
            net1 = nwObject.getNetClass(droid, 0)
            droid.log("sim1 net=" + str(net1))
        elif net2 == "UNKNOW":
            droid.log("main card sim2 no service, wait 20s,check again")
            time.sleep(20)
            net2 = nwObject.getNetClass(droid, 1)
            droid.log("sim2 net=" + str(net2))
        else:
            droid.log("have service")  
        OpenCloseSim1_OpenCloseSim2()
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
