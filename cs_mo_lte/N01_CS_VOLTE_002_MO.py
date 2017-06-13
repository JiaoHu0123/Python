'''
Created on 2016-5-10

@author: xiaoli.xia
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
#================================================================================================
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
time.sleep(10)
#==================================================================================================
droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
testTimes = config.get("Setting", "moctimes")  # get test times
hold_time = config.get("Setting", "callHoldTime")

callObject = call.MMC(scriptname=__file__)  # initial class
commObject = common.Common(scriptname=__file__)
nwObject = net.NetWork(scriptname=__file__)
droid.log("The test times is " + testTimes)
time.sleep(5)
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname;

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
    
global FlagLTE
global VolteFlag
volteFlag = False
def CheckIMS():
    sim = callObject.getMainCard(droid)
    net = nwObject.getNetClass(droid, sim)
    if net == "4G":
        FlagLTE = True
    else:
        if commObject.getDutMode(droid) != "DM":
            nwObject.startSearchNet(droid, sim)
            if nwObject.selLTE(droid, simtype):
                droid.log("SelLTE====pass")
                FlagLTE = True
            else:
                droid.log("SelLTE====fail")
                FlagLTE = False
        else:
            FlagLTE = False
            droid.log("summary:NOT_SUPPORT") 
            droid.log("the phone not support LTE")
            exit() 
    time.sleep(15)
    netFlag = nwObject.getNetClass(droid, sim)
    VolteFlag = nwObject.checkVolte(droid, sim)
    if netFlag == "4G" and VolteFlag:
        droid.log("Stay on Volte ")
        passflag = True
    else:
        droid.log("NOt stay on Volte")
        passflag = False
    return passflag
# function =================================================================================================
def mocSrvcc(droid, callNumber, testTimes, hold_time):
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test begin :")
        networkMode = droid.getCommandReturn("GetNetworkMode")
        droid.log("============netwoekMode=" + networkMode)
        droid.log("call_number=" + callNumber) 
        passFlag = callObject.voiceCall(droid, callNumber, hold_time)
        droid.log("SVRCC")
        nwObject.ATDummy_SRVCC(droid, sim)
        time.sleep(5)
        net = nwObject.getNetSate(droid, sim)
        droid.log("the net is " + net)
        if net == "GSM":
            srvcc = True
        else:
            srvcc = False
        if passFlag & srvcc:
            passTimes += 1
        else:
            failTimes += 1
        callObject.endCall(droid)
        nwObject.ATDummy_remove(droid, sim)
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
    droid.log("summary:NOT_SUPPORT") 
    exit()
    
if CheckIMS():
    droid.log("support volte")
else:
    droid.log("don't supported LTE")
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
        call_number = callObject.getCardType(droid, sim)
        callObject.setCallSim(droid, sim)
        mocSrvcc(droid, call_number, testTimes, hold_time)
    else:
        droid.log("The net is not in LTE")
        
elif cardtype == "SINGLE1":
    droid.log("***********************************only one sim card1**********************************")
    network = nwObject.getNetClass(droid, 0)
    simtype = callObject.getSimType(droid, 0)
    droid.log("the net is " + network)
    droid.log("the simtype is " + simtype)
    if network == "4G":
        call_number = callObject.getCardType(droid, 0)
        callObject.setCallSim(droid, 0)
        mocSrvcc(droid, call_number, testTimes, hold_time)
    else:
        droid.log("The net is not in LTE")
elif cardtype == "SINGLE2":
    droid.log("=====================================only one sim card2=============================") 
    network = nwObject.getNetClass(droid, 1)
    simtype = callObject.getSimType(droid, 1)
    droid.log("the net is " + network)
    droid.log("the simtype is " + simtype)
    if network == "4G":
        droid.log("=============the net is E-UTRAN,make voice call in LTE ==============")
        call_number = callObject.getCardType(droid, 1)  
        mocSrvcc(droid, call_number, testTimes, hold_time)
    else:
        droid.log("============ the net is not in LTE==========================")
else:
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT")
    exit()
commObject.result(droid,testTimes, passTimes, failTimes)
