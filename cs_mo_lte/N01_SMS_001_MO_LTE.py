'''
Created on 2016-5-1
CASE NAME:SLAB_N01_SMS_001_MO_LTE
Description: send sms on LTE network
@author: xiaoli.xia

'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import android
import ConfigParser  # get config file data
import os, sys  # use for path
import time  # use for time

# define vars
caseTimeOut = 200
config = ConfigParser.ConfigParser()
BASE_DIR = os.path.dirname(__file__)  # test scripts path name   #get parent path 
parent_dir = os.path.split(BASE_DIR)
Par_DIR = parent_dir[0]
Setting_path = os.path.join(Par_DIR, 'Settings.ini')
config.readfp(open(Setting_path, 'r'))
droid = android.Android(scriptname=__file__)
droid.log("parent path=" + BASE_DIR)
droid.log("parent_dir=" + Par_DIR)
basic_path = os.path.abspath(Par_DIR)
droid.log(basic_path)
sys.path.append(basic_path)
import basic.importMethod
basic.importMethod.importMethod()

from basic import common
from basic import sms
from basic import net
from basic import call
time.sleep(20)
droid.setCaseTimeOut(caseTimeOut)

global passTimes
global failTimes
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2

testTimes = config.get("Setting", "smsTimes")  # get test times
droid.log("The test times is " + testTimes)
smsObject = sms.SMS(scriptname = __file__)  # initial class
commObject = common.Common(scriptname = __file__)
nwObject = net.NetWork(scriptname = __file__)
callObject=call.MMC(scriptname = __file__) 
defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
defaultModeInt = nwObject.getModeStrToInt(defaultMode)
droid.log("the default mode int is " + str(defaultModeInt))

#==================================================================================
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname;

global NetWork, simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)

Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 1, "LTE", "SINGLE MODE", "NoVolte")
 
commObject.summary(droid, "CS", "LTE", simtype, "SMS", "SINGLE MODE", "30", SIM1Status, SIM2Status, Network1Status, Network2Status)
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
    droid.log("SUMMARY:%s:%s,%s:%s,%s:%s,%s:%s,%s:%s,%s:%s,%s:%s" % ("SERVICE", "CS", "NETWORK", "LTE", "NETWORK OPERATOR", simtype, "CARDTYPE", cardtype,"SUB SERVICE","Voice Call","DUAL MODE","L","SINGLETIME","20"))
    droid.log("summary:NOT_SUPPORT") 
    exit()     
       
if "LTE" in defaultMode:
    supportLTE = True
elif "AUTO"in defaultMode:
    droid.log("AUTOMODE")
else:
    supportLTE = False
    droid.log("supportLTE=" + str(supportLTE))
    droid.log("summary:NOT_SUPPORT") 
    # commObject.result(droid,testTimes, passTimes, failTimes)
    exit()
droid.log("supportLTE=" + str(supportLTE))

#==================================================================================
def testSMS(testTimes, num):
    for i in range(1, int(testTimes) + 1):
        global passTimes, failTimes
        droid.log("The " + str(i) + " times test beagin :")
        droid.log("get sms content from seetings")
        Content = smsObject.getContent()
        passFlag = smsObject.sendSMS(droid, num, Content)
        if passFlag:
            passTimes += 1
        else:
            failTimes += 1
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes)) 
        
def DS():
    smsNumber = smsObject.getSmsNumber(droid, 0)
    smsObject.setSMSSim(droid, 0)
    Content = smsObject.getContent()
    passFlag = smsObject.sendSMS(droid, smsNumber, Content)
    smsNumber = smsObject.getSmsNumber(droid, 1)
    smsObject.setSMSSim(droid, 1)
    passFlag1 = smsObject.sendSMS(droid, smsNumber, Content)
    if  passFlag & passFlag1:
        SMSFlag = True
    else:
        SMSFlag = False
    return SMSFlag
droid.log("check sim:")
#============================================================================================================
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("************************************pluginSim two card=================================")
    sim = callObject.getMainCard(droid)
    network = nwObject.getNetClass(droid, sim)
    simtype = callObject.getSimType(droid, sim)
    cardtype = "DUAL"
    for i in range(1, int(testTimes) + 1):
        if network == "4G":
            passFlag2 = DS()
        else:
            droid.log("need select to lte")
            nwObject.openFlm(droid)
            time.sleep(5)
            nwObject.closeFlm(droid)
            time.sleep(15)
            net = nwObject.getNetSate(droid, 0)
            if net == "4G":
                passFlag2 = DS()
            else:
                droid.log("no LTE net,exit")
        if  passFlag2:
            passTimes += 1
        else:
            failTimes += 1
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes)) 
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    droid.log("***********************************only one sim sim0**********************************")
    smsNumber = smsObject.getSmsNumber(droid, 0)
    network = nwObject.getNetClass(droid, 0)
    simtype = callObject.getSimType(droid, 0)
    cardtype = "SINGLE1"
    if network == "4G":
        testSMS(testTimes, smsNumber)
    else:
        droid.log("sel LTE first")
        testSMS(testTimes, smsNumber)
        
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("=======================================only one sim card1=============================")  
    smsNumber = smsObject.getSmsNumber(droid, 1)
    network = nwObject.getNetClass(droid, 1)
    simtype = callObject.getSimType(droid, 1)
    cardtype = "SINGLE2"
    if network == "4G":
        testSMS(testTimes, smsNumber)
    else:
        droid.log("sel LTE first")
        testSMS(testTimes, smsNumber)
else:
    droid.log("no sim card")
    network = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    # commObject.result(droid,testTimes, passTimes, failTimes)
    exit()
nwObject.backDefaultMode(droid, defaultMode, callObject.getMainCard(droid))
droid.log("====================THIS CASE TEST END============")
commObject.result(droid,testTimes, passTimes, failTimes)
