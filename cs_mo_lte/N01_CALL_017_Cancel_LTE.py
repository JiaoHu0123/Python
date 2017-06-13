'''
Created on 2016-5-1
update :2016-7-19 add summary info 

@author: xiaoli.xia
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import android
import ConfigParser  # get config file data
import os, sys  # use for path
import time  # use for time
import re  # rename slog name

# define var
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
from basic import call  
from basic import common
from basic import net
commObject = common.Common(scriptname=__file__)
droid.setCaseTimeOut(caseTimeOut)

passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
global modeFlag
testTimes = config.get("Setting", "moctimes")  # get test times
hold_time = config.get("Setting", "callHoldTime")
call_number = config.get("CallNum", "long_keep_number")

droid.log("The test times is " + testTimes)
callObject = call.MMC(scriptname=__file__)  # initial class
nwObject = net.NetWork(scriptname=__file__)
droid.log("parent path=" + BASE_DIR)
droid.log("parent_dir=" + Par_DIR)
droid.log("hold time=" + hold_time)
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname;

# network:net state
# simtype:CMCC,CUCC
# cardtype:SINGLE,DUAL
global NetWork, simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)

Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 1, "LTE", "SINGLE MODE", "NoVolte")
if Network1Status == "Network Normal" and nwObject.checkVolte(droid, sim):
    subservice = "VoLTE Call"
    print subservice;
else:
    subservice = "Voice Call"
    print subservice;
 
commObject.summary(droid, "CS", "LTE", simtype, subservice, "SINGLE MODE", hold_time, SIM1Status, SIM2Status, Network1Status, Network2Status)
if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
    
#===========================================================================================================
defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
defaultModeInt = nwObject.getModeStrToInt(defaultMode)
droid.log("the default mode int is " + str(defaultModeInt))
#================================================================================================================
    
# check whether supported LTE
if "LTE" in defaultMode:
    supportLTE = True
elif "AUTO" in defaultMode:
    droid.log("AUTO MODE")
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))

# check sim card
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    cardtype = "SINGLE1"
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "SINGLE2"
else:
    droid.log("no sim card")
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    # droid.log("SUMMARY:%s:%s,%s:%s,%s:%s,%s:%s,%s:%s,%s:%s,%s:%s" % ("SERVICE", "CS", "NETWORK", "LTE", "NETWORK OPERATOR", simtype, "CARDTYPE", cardtype))
    droid.log("summary:NOT_SUPPORT") 
    exit()     
#--------------------------------------------------------------------------------------------------
if supportLTE:
    droid.log("supported LTE")
else:
    droid.log("don't supported LTE")
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    exit()   

def dialing(network):
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test beagin :")
        passFlag = callObject.dialingCall(droid, call_number, 5)
        passFlag1 = callObject.endCall(droid) 
        if passFlag & passFlag1:
            passTimes += 1
        else:
            failTimes += 1
        time.sleep(10)
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   
        
# check sim card
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("pluginSim two card")
    cardtype = "DUAL"
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test beagin :")
        sim = callObject.getMainCard(droid)
        network = nwObject.getNetClass(droid, sim)
        simtype = callObject.getSimType(droid, sim)
        if "4G" == network:
            registeLTE = True
            droid.log("stay on LTE")
        else:
            registeLTE = False
            droid.log("don't stay on LTE")
            simtype = callObject.getSimType(droid, sim)
            nwObject.startSearchNet(droid, sim)
            
            nwObject.selLTE(droid, simtype)
            time.sleep(30)
        callObject.setCallSim(droid, sim)  # set call card sim1
        passFlag = callObject.dialingCall(droid, call_number, 5)
        print passFlag
        passFlag1 = callObject.endCall(droid)
        if passFlag & passFlag1:
            passTimes += 1
        else:
            failTimes += 1
        time.sleep(10)
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))

elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    droid.log("***********************************only one sim **********************************")
    cardtype = "SINGLE1"
    network = nwObject.getNetClass(droid, 0)
    simtype = callObject.getSimType(droid, 0)
    droid.log("the net is " + network)
    droid.log("the simtype is " + simtype)
    dialing(network)
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("***********************************only one sim **********************************")
    cardtype = "SINGLE2"
    network = nwObject.getNetClass(droid, 1)
    simtype = callObject.getSimType(droid, 1)
    droid.log("the net is " + network)
    droid.log("the simtype is " + simtype)
    dialing(network)
else:
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT") 
    # commObject.result(droid,testTimes, passTimes, failTimes)
    exit()
nwObject.backDefaultMode(droid, defaultModeInt, sim)
droid.log("=============THIS CASE TEST END==============")
commObject.result(droid,testTimes, passTimes, failTimes)
