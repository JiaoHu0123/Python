#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-15

@author: zhaoxia.zhang
CaseName: 
Fuction: 
    Main Card: Sim2 ,Data Card: Sim2
    SLAB_N05_Interaction_2SIM_958_Sim1EMC_Sim2SMS_11_IMS
'''
import android
import ConfigParser  # get config file data
import os, sys, time  # use for path
#================================================================================================
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
from basic import sms
time.sleep(10)
#==================================================================================================
droid.setCaseTimeOut(caseTimeOut)

passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
global network, simtype, cardtype
testTimes = config.get("Setting", "emcTimes")  # get test times
hold_time = config.get("Setting", "callHoldTime")
droid.log("The test times is " + testTimes)
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname

smsObject = sms.SMS(scriptname=__file__)
callObject = call.MMC(scriptname=__file__)  # initial class
commObject = common.Common(scriptname=__file__)
nwObject = net.NetWork(scriptname=__file__)
time.sleep(5)
#===network=====================================================================================================
sim = callObject.getMainCard(droid)
network = nwObject.getNetClass(droid, sim)
simtype = callObject.getSimType(droid, sim)
#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "LTE", "L+G", "SingleVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "IMS", "LTE", simtype, "Emergency Call", "L+G", "20", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================

defaultMode = droid.getCommandReturn("GetnetworkMode")
droid.log("===================defualtMode=" + defaultMode)
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
else:
    defaultModeInt = nwObject.getModeStrToInt(defaultMode)
    droid.log("the default mode int is " + str(defaultModeInt))

nwObject.getModeType(droid)

if "LTE" in defaultMode:
    supportLTE = True
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))

cardtype = "DUAL"
# check whether supported volte
if nwObject.checkVolte(droid, sim):
    supportVolte = True
else:
    supportVolte = False
    droid.log("summary:NOT_SUPPORT") 
    exit() 
droid.log("supportVolte=" + str(supportVolte))
#========================================================================================================
    
def EmcSms(droid, callNumber, smsNumber, testTimes, hold_time):
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):    
        droid.log("The " + str(i) + " times test begin :")
        droid.log("Emc_number=" + callNumber) 
        passFlag = callObject.emcCall(droid, callNumber, hold_time)
        callObject.endCall(droid)
        droid.log("sms_number=" + smsNumber)
        Content = smsObject.getContent()
        passFlag1 = smsObject.sendSMS(droid, smsNumber, Content)
        time.sleep(10)
        if passFlag & passFlag1:
            passTimes += 1
        else:
            failTimes += 1
        callObject.endCall(droid)
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   

#================================================================================================================
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)
network = nwObject.getNetClass(droid, sim)
# check sim card
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
    droid.log("********************pluginSim two card=============================")
    # pre condicton
    callObject.setMainCard(droid, 1)
    time.sleep(30)
    callObject.setDataCard(droid, 1)
    time.sleep(30)
    # get net state
    simType1 = callObject.getSimType(droid, 0)
    simType2 = callObject.getSimType(droid, 1)
    droid.log("sim1Type =" + simType1 + "sim2Type=" + simType2)
    nwObject.searchingNet(droid, 1)
    nwObject.selLTE(droid, simType2)
    nwObject.checkVolte(droid, 1)
    net1 = nwObject.getNetClass(droid, 0)
    net2 = nwObject.getNetClass(droid, 1)
    droid.log("sim1 network=" + net1 + "sim2 network=" + net2)
    # function EMC SMS
    emcNumber = config.get("CallNum", "emc")
    smsObject.setSMSSim(droid, 1)  # Sim2 SMS
    sms_number = smsObject.getSmsNumber(droid, 1)  # SIM2 send sms
    EmcSms(droid, emcNumber, sms_number, testTimes, hold_time)
    time.sleep(30)
    callObject.setMainCard(droid, 0)
    time.sleep(30)
    callObject.setDataCard(droid, 0)
    # update
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    cardtype = "SINGLE1"
    droid.log("only one sim card1")
    droid.log("summary:NOT_SUPPORT")
    exit()
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "SINGLE2"
    droid.log("only one sim card2")
    droid.log("summary:NOT_SUPPORT")
    exit()
else:
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    droid.log("summary:NOT_SUPPORT")
    exit()
droid.log("=============THIS CASE TEST END==============")
commObject.result(droid,testTimes, passTimes, failTimes)
