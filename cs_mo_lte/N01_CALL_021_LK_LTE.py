#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-3-18

@author: xiaoli.xia
CaseName: 

'''
import android
import ConfigParser  # get config file data
import os, sys, time  # use for path

# define vars
caseTimeOut = 200
config = ConfigParser.ConfigParser()
BASE_DIR = os.path.dirname(__file__)  # test scripts path name   #get parent path 
parent_dir = os.path.split(BASE_DIR)
Par_DIR = parent_dir[0]
Setting_path = os.path.join(Par_DIR, 'Settings.ini')
config.readfp(open(Setting_path, 'r'))
droid = android.Android(scriptname=__file__)
#================================================================================================
# import the basic 
basic_path = os.path.abspath(Par_DIR)
droid.log(basic_path)
sys.path.append(basic_path)
import basic.importMethod
basic.importMethod.importMethod()
from basic import call  
from basic import common
from basic import net
time.sleep(10)
#==================================================================================================
droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
testTimes = config.get("Setting", "lkTimes")  # get test times
lk_time = config.get("Setting", "longcallTime")
callObject = call.MMC(scriptname=__file__)  # initial class
commObject = common.Common(scriptname=__file__)
nwObject = net.NetWork(scriptname=__file__)
droid.log("The test times is " + testTimes)
call_number = config.get("CallNum", "long_keep_number")
time.sleep(5)
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
 
commObject.summary(droid, "CS", "LTE", simtype, subservice, "SINGLE MODE", lk_time, SIM1Status, SIM2Status, Network1Status, Network2Status)
if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#==================================================================================================    
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname;
defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)

if "LTE" in defaultMode:
    supportLTE = True
else:
    supportLTE = False
    droid.log("summary:NOT_SUPPORT") 
    exit()
droid.log("supportLTE=" + str(supportLTE))
#==================================================================================================
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
defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)

# function =================================================================================================
 
def longMoc(callNumber, testTimes, lk_time):
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):
        global noCallDrop
        droid.log("The " + str(i) + " times test begin :")
        networkMode = droid.getCommandReturn("GetNetworkMode")
        droid.log("============netwoekMode=" + networkMode)
        droid.log("call_number=" + callNumber) 
        passFlag = callObject.longCall(droid, callNumber, lk_time)
        droid.log("keep lk_time=" + str(lk_time))
        lk_time = int(lk_time) / 10
        droid.log("check times =" + str(lk_time))
        for j in range(1, int(lk_time)):
            time.sleep(10)
            droid.log("check call state,after " + str(j * 10) + " time")
            passFlag1 = callObject.checkCallState(droid)
            if passFlag1:
                droid.log("no call drop")
                noCallDrop = True
            else:
                droid.log("call drop,")
                noCallDrop = False
                break
        if passFlag & noCallDrop:
            passTimes += 1
        else:
            failTimes += 1
        callObject.endCall(droid)
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   

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
    
#================================================================================================================
# check sim card
if cardtype == "DUAL":
    droid.log("********************pluginSim two card=============================")
    sim = callObject.getMainCard(droid)
    network = nwObject.getNetClass(droid, sim)
    simtype = callObject.getSimType(droid, sim)
    if network == "4G":
        callObject.setCallSim(droid, sim)
        longMoc(call_number, testTimes, lk_time)
    else:
        droid.log("The net is not in LTE")
elif cardtype == "SINGLE1":
    droid.log("***********************************only one sim card1**********************************")
    network = nwObject.getNetClass(droid, 0)
    simtype = callObject.getSimType(droid, 0)
    if network == "4G":
        callObject.setCallSim(droid, 0)
        longMoc(call_number, testTimes, lk_time)
    else:
        droid.log("The net is not in LTE")

elif cardtype == "SINGLE2":
    print droid.log("=====================================only one sim card2=============================") 
    network = nwObject.getNetClass(droid, 1)
    simtype = callObject.getSimType(droid, 1)
    if network == "4G":
        droid.log("=============the net is E-UTRAN,make voice call in LTE ==============")
        callObject.setCallSim(droid, 1)
        longMoc(call_number, testTimes, lk_time)
    else:
        droid.log("============ the net is not in LTE==========================")
else:
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT") 
    # commObject.result(droid,testTimes, passTimes, failTimes)
    exit()
commObject.result(droid, testTimes, passTimes, failTimes)
