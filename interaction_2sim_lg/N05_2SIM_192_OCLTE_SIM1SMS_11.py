#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-6-25

@author: panpan.wei: 
Fuction:sim2 main card,sim2 data card, sim2 close lte, sim1 sms and sim2 open lte, sim1 sms
 update date 2016-07-15
 update 4m and 5m ,3m ok
'''
import android
import ConfigParser  # get config file data
import os, sys  # use for path
# define vars
# import the basic 
droid = android.Android(scriptname=__file__)
droid.log("import basic file")
config = ConfigParser.ConfigParser()
BASE_DIR = os.path.dirname(__file__)  # test scripts path name   #get parent path 

parent_dir = os.path.split(BASE_DIR)
Par_DIR = parent_dir[0]


Setting_path = os.path.join(Par_DIR, 'Settings.ini')
config.readfp(open(Setting_path, 'r'))
basic_path = os.path.abspath(Par_DIR)
droid.log(basic_path)
sys.path.append(basic_path)
droid.log("import the method")
import basic.importMethod
basic.importMethod.importMethod()
droid.log("import the call")
from basic import call  
droid.log("mport the common")
from basic import common
from basic import net
from time import sleep
from basic import  ps
from basic import sms
import time
droid.log("import file finish")
time.sleep(10)
caseTimeOut = 200



defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)


droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
testTimes = config.get("Setting", "interaction")  # get test times
callObject=call.MMC(scriptname = __file__)   # initial class
commObject = common.Common(scriptname = __file__)
# sheetobj=Workbook.WorkSheet()
nwObject = net.NetWork(scriptname = __file__)
psObject = ps.PS(scriptname = __file__)
smsObject = sms.SMS(scriptname = __file__)
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname
droid.log("The test times is " + testTimes)
time.sleep(5)
webSite = config.get("BrowserAdd", "wapAddress") 
defaultModeInt = nwObject.getModeStrToInt(defaultMode)
droid.log("the default mode int is " + str(defaultModeInt))

# function =================================================================================================
global  simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)
netWork = nwObject.getNetClass(droid, sim)

#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "MULTI", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}
 
commObject.summary(droid, "INTERACTION", "MULTI", simtype, "4G Swith", "L+G", "120", SIM1Status, SIM2Status, Network1Status, Network2Status)
 
if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================
 
if ("LTE" in defaultMode) or ("4m" in version) or ("5m" in version):
    droid.log("supported LTE")
else:
    droid.log("don't supported LTE")
    droid.log("summary:NOT_SUPPORT")
    exit()
 
def SMS():
    Content = smsObject.getContent()
    smsNumber = smsObject.getSmsNumber(droid, 0)  # sim1 send sms
    smsObject.setSMSSim(droid, 0)
    passFlag = smsObject.sendSMS(droid, smsNumber, Content)
    return passFlag
 
def OpenCloseLTE_SIM1SMS():
    global passTimes, failTimes
    closelte = False
    openlte = False
    sim = callObject.getMainCard(droid)
    netClass = nwObject.getNetClass(droid, sim)
    if netClass == "4G":
        droid.log("===========MainCard==" + str(sim) + "====NetClass===" + netClass) 
        closelte = nwObject.closeLte(droid)
        sms1 = SMS()
        openlte = nwObject.openLte(droid)
        sms2 = SMS()
        droid.log("=========" + str(closelte) + "=============" + str(openlte))
        sleep(20)
        droid.log("===========Sleep(10)===========")
        if closelte & openlte & sms1 & sms2:
            droid.log("=============Data_pass_and_SMS_pass=================")
            passTimes += 1
        else:
            droid.log("=============Data_fail_and_SMS_fail=================")
            failTimes += 1 
    else:
        droid.log("the net is not 4G")
 
 
 
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
    droid.log("************************************pluginSim two card=================================")
    callObject.setPreCondition(droid, 1, 1)
    sleep(60)
    for i in range(1, int(testTimes) + 1):   
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
        OpenCloseLTE_SIM1SMS()
    droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))       
    callObject.setPreCondition(droid, 0, 0)
    sleep(30) 
     
    # update:panbing
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
