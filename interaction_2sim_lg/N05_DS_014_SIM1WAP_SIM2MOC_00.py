#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-3-18

@author: xiaoli.xia
CaseName: 
Fuction: 
    SIM1 MAIN CARD,SIM1 DATA CARD
    SIM1 WAP,SIM2 MOC
    SLAB_N05_Interaction_2SIM_014_WAP_MOC
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
import basic.importMethod
basic.importMethod.importMethod()
from basic import net
from basic import ps
from basic import call
from basic import common
droid.log("======================import file finish=======================")
time.sleep(10)
#==================================================================================================
droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
testTimes = config.get("Setting", "interaction")  # get test times
hold_time = config.get("Setting", "callHoldTime")
website = config.get("BrowserAdd", "wapAddress")

callObject=call.MMC(scriptname = __file__)   # initial class
commObject = common.Common(scriptname = __file__)
nwObject = net.NetWork(scriptname = __file__)
psObject = ps.PS(scriptname = __file__)
DUAL = False
droid.log("The test times is " + testTimes)
time.sleep(5)
nwObject.checkMode(droid)
defaultModeInt = nwObject.getModeStrToInt(defaultMode)
droid.log("the default mode int is " + str(defaultModeInt))

global simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)
netWork = nwObject.getNetClass(droid, sim)

#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "LTE", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "INTERACTION", "LTE", simtype, "Voice Call", "L+G", "30", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================

if "LTE" in defaultMode:
    supportLTE = True
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))
# function =================================================================================================
def WAP():
    wapFlag = psObject.ConnectInternet(droid, website)
    return wapFlag

def WAP_MOC(droid, callNumber, testTimes, hold_time):
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test begin :")
        sim1type = callObject.getSimType(droid, 0)
        sim2type = callObject.getSimType(droid, 1)
        droid.log("sim1 simtype=" + sim1type + ";sim2 simtype=" + sim2type)
        net1 = nwObject.getNetClass(droid, 0)
        net2 = nwObject.getNetClass(droid, 1)
        droid.log("sim1 network=" + net1 + ";sim2 network=" + net2)
        if net1 == "UNKNOW":
            droid.log("main card sim1 no service,wait 20s,check again")
            time.sleep(20)
            net1 = nwObject.getNetClass(droid, 0)
            droid.log("sim1 net=" + str(net1))
        else:
            droid.log("have service")
        wapFlag = WAP()
        networkMode = droid.getCommandReturn("GetNetworkMode")
        droid.log("============netwoekMode=" + networkMode)
        droid.log("call_number=" + callNumber) 
        passFlag = callObject.voiceCall(droid, callNumber, hold_time)
        if passFlag & wapFlag:
            passTimes += 1
        else:
            failTimes += 1
        callObject.endCall(droid)
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   
#================================================================================================================
# check sim card

if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    print droid.log("********************pluginSim two card=============================")
    droid.log("set sim1 as main card,data card;and wait 20s")
    callObject.setPreCondition(droid, 0, 0)
    time.sleep(20)
    DUAL = True
    net = nwObject.getNetSate(droid, 0)
    droid.log("the net is " + net)
    call_number = callObject.getCardType(droid, 1)
    WAP_MOC(droid, call_number, testTimes, hold_time)
    cardtype = "DUAL"  
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    droid.log("summary:NOT_SUPPORT")
    droid.log("only one sim card1")
    cardtype = "SINGLE1"
    netWork = nwObject.getNetClass(droid, 0)
    simtype = callObject.getSimType(droid, 0)
    exit()

elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("summary:NOT_SUPPORT")
    droid.log("only one sim card2")
    cardtype = "SINGLE2"
    netWork = nwObject.getNetClass(droid, 1)
    simtype = callObject.getSimType(droid, 1)
    exit()
else:
    droid.log("summary:NOT_SUPPORT")
    droid.log("no sim card")
    netWork = "NO_NET"
    simtype = "NO_SIM"
    cardtype = "NO_SIM"
    exit()
droid.log("=============THIS CASE TEST END==============")
commObject.result(droid,testTimes, passTimes, failTimes)
