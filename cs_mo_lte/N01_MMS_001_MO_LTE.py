#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-6-25

@author: panbin.ai
CaseName: N01_MMS_MO_LTE
Fuction: 
    mms
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
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname
defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
#================================================================================================
# import the basic 
droid.log("===================import basic file")
basic_path = os.path.abspath(Par_DIR)
droid.log(basic_path)
sys.path.append(basic_path)
from basic import call  
from basic import common
from basic import net
from basic import sms
from basic import ps
droid.log("======================import file finish=======================")
#==================================================================================================
droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
global simtype, cardtype

testTimes = config.get("Setting", "interaction")  # get test times
smsObject = sms.SMS(scriptname=__file__)
callObject = call.MMC(scriptname=__file__)  # initial class
commObject = common.Common(scriptname=__file__)
nwObject = net.NetWork(scriptname=__file__)
psObject = ps.PS(scriptname=__file__)
droid.log("The test times is " + testTimes)
# function =================================================================================================
global simtype, cardtype, netWork
sim = callObject.getMainCard(droid)
network = nwObject.getNetClass(droid, sim)
simtype = callObject.getSimType(droid, sim)

Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 1, "LTE", "SINGLE MODE", "NoVolte")

commObject.summary(droid, "CS", "LTE", simtype, "MMS", "SINGLE MODE", "30", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("SIM Status Is ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")

defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
defaultModeInt = nwObject.getModeStrToInt(defaultMode)

def MMS():
    global passTimes
    global failTimes
    smsnumber = callObject.getCardType(droid, callObject.getMainCard(droid))
    smsObject.setSMSSim(droid, int(sim))
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test begin :")
        passFlag = smsObject.SendMMS(droid, smsnumber)
        time.sleep(30)
        if passFlag:
            passTimes += 1
        else:
            failTimes += 1
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   
#================================================================================================================
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAl"
    droid.log("********************pluginSim two card=============================")
    MMS()
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    MMS()
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    MMS()
else:
    droid.log("no sim card")
    droid.log("summary:NOT_SUPPORT") 
    exit()
droid.log("=============THIS CASE TEST END==============")
commObject.result(droid, testTimes, passTimes, failTimes)
