#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-3-18

@author: xiaoli.xia

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
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname;

basic_path = os.path.abspath(Par_DIR)
droid.log(basic_path)
sys.path.append(basic_path)
import basic.importMethod
basic.importMethod.importMethod()
from basic import call  
from basic import common
from basic import net
droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
testTimes = config.get("Setting", "emcTimes")  # get test times
emcNum = config.get("CallNum", "emc")
hold_time = config.get("Setting", "callHoldTime")
droid.log("The test times is " + testTimes)
droid.log("parent path=" + BASE_DIR)
droid.log("parent_dir=" + Par_DIR)
droid.log("hold time=" + hold_time)

callObject=call.MMC(scriptname = __file__)   # initial class
commObject = common.Common(scriptname = __file__)
nwObject = net.NetWork(scriptname = __file__)

global NetWork, simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)

Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 1, "LTE", "SINGLE MODE", "NoVolte")
commObject.summary(droid, "CS", "LTE", simtype, "Emergency Call", "SINGLE MODE", hold_time, SIM1Status, SIM2Status, Network1Status, Network2Status)
if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")

defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
if "LTE" in defaultMode:
    supportLTE = True
elif "AUTO" in defaultMode:
    droid.log("AUTO MODE")
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))

mode = commObject.getDutMode(droid)
if mode == "5M":
    defaultModeInt = nwObject.getModeStrToInt(defaultMode)
    if defaultModeInt != 18:
        droid.log("set to 5M")
        nwObject.setMode5M(droid)
        droid.log("wait 30s")
        time.sleep(30)
    else:
        droid.log("the mode is 5M")
elif mode == "4M":
    defaultModeInt = nwObject.getModeStrToInt(defaultMode)
    if defaultModeInt != 13:
        droid.log("set to W4M")
        nwObject.setModeW4M(droid)
    else:
        droid.log("the mode is W4M")
else:
    defaultModeInt = nwObject.getModeStrToInt(defaultMode)
    droid.log("the default mode int is " + str(defaultModeInt))

#============================================================================================================
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
    
if "LTE" in defaultMode:
    supportLTE = True
elif "AUTO" in defaultMode:
    droid.log("AUTO MODE")
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))

if supportLTE:
    droid.log("supported LTE")
else:
    droid.log("don't supported LTE")
    exit()
#================================================================================================================
for i in range(1, int(testTimes) + 1):
    droid.log("The " + str(i) + " times test beagin :")
    sim = callObject.getMainCard(droid)
    network = nwObject.getNetClass(droid, sim)
    simtype = callObject.getSimType(droid, sim)
    cardtype = "DUAL"
    if "4G" == network:
        registeLTE = True
        droid.log("stay on LTE")
    else:
        registeLTE = False
        droid.log("don't stay on LTE")
    droid.log("call_number=" + emcNum)
    passFlag = callObject.emcCall(droid, emcNum, hold_time)
    if passFlag:
        passTimes += 1
    else:
        failTimes += 1
    callObject.endCall(droid)
    droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   
# set back to default mode
nwObject.backDefaultMode(droid, defaultModeInt, callObject.getMainCard(droid))
droid.log("============ TEST END====================")
commObject.result(droid,testTimes, passTimes, failTimes)
