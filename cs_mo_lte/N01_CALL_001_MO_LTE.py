#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-3-18

@author: xiaoli.xia
CaseName: 
Fuction: 
    make voice call
update :2016-7-19 add summary info 
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
droid.log("==============Par_DIR==" + Par_DIR)
defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
#================================================================================
# import the basic
droid.log("===================import basic file")
basic_path = os.path.abspath(Par_DIR)
droid.log(basic_path)
sys.path.append(basic_path)
droid.log("====================import the method")
import basic.importMethod
basic.importMethod.importMethod()
droid.log("====================import the call")
from basic import call  
droid.log("====================import the common")
from basic import common
from basic import net
droid.log("====================import file finish")
time.sleep(10)
#=================================================================================
droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
testTimes = config.get("Setting", "mocTimes")  # get test times from configer file Setting
hold_time = config.get("Setting", "callHoldTime")

callObject = call.MMC(scriptname=__file__)  # initial class
commObject = common.Common(scriptname=__file__)
nwObject = net.NetWork(scriptname=__file__)
droid.log("The test times is " + testTimes)
time.sleep(5)
droid.log("#=========================================================================")
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname;

defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
defaultModeInt = nwObject.getModeStrToInt(defaultMode)
droid.log("the default mode int is " + str(defaultModeInt))

# function ============================================================================
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
else:
    supportLTE = False
    droid.log("summary:NOT_SUPPORT") 
    exit()
droid.log("supportLTE=" + str(supportLTE))
       
def moc(droid, callNumber, testTimes, hold_time):
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test begin :")
        networkMode = droid.getCommandReturn("GetNetworkMode")
        droid.log("============netwoekMode=" + networkMode)
        droid.log("call_number=" + callNumber) 
        passFlag = callObject.voiceCall(droid, callNumber, hold_time)
        if passFlag:
            passTimes += 1
        else:
            failTimes += 1
        callObject.endCall(droid)
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   
#================================================================================================================
# check sim card
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("********************pluginSim two card=============================")
    sim = callObject.getMainCard(droid)
    net = nwObject.getNetClass(droid, sim)
    # update 2016-7-19 xiaoli
    network = nwObject.getNetSate(droid, sim)
    simtype = callObject.getSimType(droid, sim)
    cardtype = "DUAL"
    VOLTE = nwObject.checkVolte(droid, sim)
    droid.log("the net is " + net)
    if net == "4G":
        call_number1 = callObject.getCardType(droid, 0)
        call_number2 = callObject.getCardType(droid, 1)
        callObject.setCallSim(droid, 0)
        callNumber = callObject.getCardType(droid, sim) 
        moc(droid, callNumber, testTimes, hold_time)
    else:
        droid.log("The net is not in LTE")
        droid.log("summary:NOT_SUPPORT") 
        # commObject.result(droid,testTimes, passTimes, failTimes)
        exit()
       
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    droid.log("***********************************only one sim card1**********************************")
    cardtype = "SINGLE1"
    network = nwObject.getNetSate(droid, 0)
    simtype = callObject.getSimType(droid, 0)
    droid.log("the net is " + network)
    droid.log("the simtype is " + simtype)
    net = nwObject.getNetClass(droid, 0)
    if net == "4G":
        call_number = callObject.getCardType(droid, 0)
        callObject.setCallSim(droid, 0)
        moc(droid, call_number, testTimes, hold_time)
    else:
        droid.log("The net is not in LTE")
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("=====================================only one sim card2=============================") 
    cardtype = "SINGLE2"
    network = nwObject.getNetSate(droid, 1)
    simtype = callObject.getSimType(droid, 1)
    net = nwObject.getNetClass(droid, 0)
    if net == "4G":
        droid.log("=============the net is E-UTRAN,make voice call in LTE ==============")
        call_number = callObject.getCardType(droid, 1)  
        moc(droid, call_number, testTimes, hold_time)
    else:
        droid.log("============ the net is not in LTE==========================")
else:
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT") 
    exit()
# nwObject.backDefaultMode(droid, defaultModeInt, callObject.getMainCard(droid))
nwObject.backDefaultMode(droid, defaultModeInt, callObject.getMainCard(droid))
droid.log("=============THIS CASE TEST END==============")
commObject.result(droid, testTimes, passTimes, failTimes)
