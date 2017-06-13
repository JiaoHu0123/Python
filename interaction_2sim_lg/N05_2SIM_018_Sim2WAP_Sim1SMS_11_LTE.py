#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-13

@author: panpan.wei
ScriptName:
Function:  (LTE)sim2  is main card and sim2 is data card, Sim2 WAP and Sim1 SMS
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
from basic import ps
droid.setCaseTimeOut(caseTimeOut)


passTimes = 0
failTimes = 0
phoneId = 1  # 0-sim1;1-sim2
testTimes = config.get("Setting", "interaction")  # get test times
hold_time = config.get("Setting", "callHoldTime")
emcNum = config.get("CallNum", "emc")
website = config.get("BrowserAdd", "wapAddress")

droid.log("The test times is " + testTimes)
nwObject = net.NetWork(scriptname = __file__)
commObject = common.Common(scriptname = __file__)
callObject=call.MMC(scriptname = __file__) 
smsObject = sms.SMS(scriptname = __file__) 
psObject = ps.PS(scriptname = __file__)
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
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "LTE", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "INTERACTION", "LTE", simtype, "SMS", "L+G", "30", SIM1Status, SIM2Status, Network1Status, Network2Status)

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
    supportLTE = True
    droid.log("AUTO MODE")
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))

if network == "4G" :
    networkok = True
elif supportLTE:
        nwObject.startSearchNet(droid, sim)
        network = nwObject.selLTE(droid, simtype)
        networkok = True
else:
        networkok = False
        droid.log("---------There is no lte-------------")
        droid.log("summary:NOT_SUPPORT")
        exit()


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

def SMS():
    Content = smsObject.getContent()
    smsNumber = smsObject.getSmsNumber(droid, 0)  # sim1 send sms
    smsObject.setSMSSim(droid, 0)
    passFlag = smsObject.sendSMS(droid, smsNumber, Content)
    return passFlag
    
# close sim1 ,sim2 moc,open sim1
def WAP_SMS():
    global passTimes, failTimes
    callObject.setMainCard(droid, 1)
    time.sleep(30)
    callObject.setDataCard(droid, 1)
    time.sleep(20)
    for i in range(1, int(testTimes) + 1):
        droid.log("This is the " + str(i) + " times test:")
        passFlag1 = psObject.ConnectInterneting(droid, website)
        time.sleep(20)
        passFlag = SMS()
        time.sleep(20)
        droid.log("===wap=" + str(passFlag1) + "====sms=" + str(passFlag))
        if passFlag & passFlag1:
            passTimes += 1
        else:
            failTimes += 1
    droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))  
    callObject.setPreCondition(droid, 0, 0) 
    time.sleep(30)

#============================================================================================================
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK") and networkok:
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
        WAP_SMS()
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    cardtype = "SINGLE1"
    droid.log("summary:NOT_SUPPORT")  
    exit()
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "SINGLE2"
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
