'''
Created on 2016-5-10
Function: VOLTE CALL and srvcc by at dummy
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
droid.log("=defualtMode=" + defaultMode)
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
droid.log("====================import file finish")
time.sleep(10)
#==================================================================================================
droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes,call_number
testTimes = config.get("Setting", "vtTimes")  # get test times
hold_time = config.get("Setting", "callHoldTime")
# call_number=config.get("CallNum", "vt_callnum")

callObject=call.MMC(scriptname = __file__)   # initial class
commObject = common.Common(scriptname = __file__)
nwObject = net.NetWork(scriptname = __file__)
droid.log("The test times is " + testTimes)
time.sleep(5)
call_number = callObject.getVTNumber(droid)
defaultModeInt = nwObject.getModeStrToInt(defaultMode)
droid.log("the default mode int is " + str(defaultModeInt))
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname
# function =================================================================================================
# check register network
global NetWork, simtype, cardtype
sim = callObject.getMainCard(droid)
network = nwObject.getNetClass(droid, sim)
simtype = callObject.getSimType(droid, sim)
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 1, "LTE", "SINGLE MODE", "SingleVolte")
 
commObject.summary(droid, "CS", "LTE", simtype, "Video Call", "SINGLE MODE", hold_time, SIM1Status, SIM2Status, Network1Status, Network2Status)
if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")

if "LTE" in defaultMode:
    supportLTE = True
    droid.log("supportLTE=" + str(supportLTE))
elif "AUTO" in defaultMode:
    droid.log("AUTO MODE")
else:
    droid.log("summary:NOT_SUPPORT")
    supportLTE = False
    exit()
    
def CheckIMS():
    global FlagLTE
    global FlagVOLTE
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
    if VolteFlag:
        droid.log("support volte")
    else:
        droid.log("summary:NOT_SUPPORT") 
        droid.log("the phone not support LTE")
        exit() 
    if netFlag == "4G" and VolteFlag:
        droid.log("Stay on Volte ")
        passflag = True
    else:
        droid.log("NOt stay on Volte")
        passflag = False    
    return passflag

def VoLTESrvcc(droid, testTimes, hold_time):
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test begin :")
        networkMode = droid.getCommandReturn("GetNetworkMode")
        droid.log("============netwoekMode=" + networkMode)
      
        sim = callObject.getMainCard(droid)
        if CheckIMS():
            passFlag = callObject.voiceCall(droid, call_number, hold_time)
            droid.log("SVRCC")
            nwObject.ATDummy_SRVCC(droid, sim)
            droid.log("wait 53s")
            time.sleep(53)
            net = nwObject.getNetSate(droid, sim)
            droid.log("the net is " + net)
            if passFlag:
                passTimes += 1
            else:
                failTimes += 1
            callObject.endCall(droid)
            time.sleep(5)
            nwObject.ATDummy_SRVCC_remove(droid,sim)
            time.sleep(15)
        else:
            droid.log("no 4G net")
            droid.log("the case test fail ")
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   

#================================================================================================================
# check sim card

if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("********************pluginSim two card=============================")
    cardtype = "DUAL"
    sim = callObject.getMainCard(droid)
    network = nwObject.getNetSate(droid, sim)
    simtype = callObject.getSimType(droid, int(sim))
    net = nwObject.getNetClass(droid, sim)
    droid.log("the net is " + net)
    callObject.setCallSim(droid, sim)
    call_number = callObject.getCardType(droid, sim) 
    if CheckIMS():
        VoLTESrvcc(droid, testTimes, hold_time)
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    print droid.log("***********************************only one sim card1**********************************")
    net = nwObject.getNetClass(droid, 0)
    droid.log("the net is " + net)
    cardtype = "SINGLE1"
    network = nwObject.getNetSate(droid, sim)
    simtype = callObject.getSimType(droid, 0)
    call_number = callObject.getCardType(droid, 0)
    callObject.setCallSim(droid, 0)
    if CheckIMS():
        VoLTESrvcc(droid, testTimes, hold_time)
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    print droid.log("=====================================only one sim card2=============================") 
    net = nwObject.getNetClass(droid, 1)
    droid.log("the net is " + net)
    cardtype = "SINGLE2"
    network = nwObject.getNetSate(droid, 1)
    simtype = callObject.getSimType(droid, 1)
    call_number = callObject.getCardType(droid, 1)
    callObject.setCallSim(droid, 1)
    if CheckIMS():
        VoLTESrvcc(droid, testTimes, hold_time)
else:
    print droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT") 
    exit()
commObject.result(droid,testTimes, passTimes, failTimes)
