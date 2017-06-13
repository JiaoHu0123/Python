#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-13
@author: panbin.ai
CaseName: 
    SLAB_N05_Interaction_DS_588_Sim2ExchangeDataCard_Sim1SMS_IMS_11
Fuction: 
    SIM2 MAIN CARD,SIM2 DATA CARD
    Sim2ExchangeDataCard_Sim1SMS
'''
import android
import ConfigParser  # get config file data
import os, sys, time  # use for path
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
droid.log("import the common")
from basic import common
from basic import net
from basic import ps
from basic import sms
from time import sleep

passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
global netWork, simtype, cardtype
testTimes = config.get("Setting", "interaction")  # get test times
droid.log("The test times is " + testTimes)
nwObject = net.NetWork(scriptname = __file__)
commObject = common.Common(scriptname = __file__)
callObject=call.MMC(scriptname = __file__) 
smsObject = sms.SMS(scriptname = __file__)
holdTime = config.get("Setting", "callHoldTime")
Content = smsObject.getContent()
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname
#===================================================
global simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)
    
#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "LTE", "L+G", "SingleVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "IMS", "LTE", simtype, "Data Switch", "L+G", "60", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================
def SelLTE(sim):
    sim = callObject.getMainCard(droid)
    net = nwObject.getNetClass(droid, sim)
    if net == "4G":
        return True
    else:
        if commObject.getDutMode(droid) != "DM":
            nwObject.startSearchNet(droid, sim)
            if nwObject.selLTE(droid, simtype):
                droid.log("SelLTE====pass")
                return True
            else:
                droid.log("SelLTE====fail")
                return False
        else:
            droid.log("summary:NOT_SUPPORT") 
            droid.log("the phone not support LTE")    
#===================================================
def CheckIMS(sim):
    netFlag = nwObject.getNetClass(droid, sim)
    VolteFlag = nwObject.checkVolte(droid, sim)
    if netFlag == "4G" and VolteFlag:
        droid.log("Stay on Volte ")
        return True
    else:
        droid.log("summary:NOT_SUPPORT") 
        droid.log("NOt stay on Volte")
        return False
#===================================================
def SMS_ChangeDataCard(smsNum, sim):
    global passTimes, failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("This is the " + str(i) + "times test:")
        simType1 = callObject.getSimType(droid, 0)
        simType2 = callObject.getSimType(droid, 1)
        droid.log("sim1Type =" + simType1 + "  sim2Type=" + simType2)
        net1 = nwObject.getNetClass(droid, 0)
        net2 = nwObject.getNetClass(droid, 1)
        droid.log("sim1 network=" + net1 + "sim2 network=" + net2)
        smsflag = smsObject.sendSMS(droid, smsNum, Content)
        changeDataCardFlag = callObject.setDataCard(droid, sim)
        droid.log("emcflag===" + str(smsflag) + "  changeDataCardFlag===" + str(changeDataCardFlag))
        time.sleep(5)
        if  smsflag and changeDataCardFlag:
            passTimes += 1
        else:
            failTimes += 1
        droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))   
        callObject.setPreCondition(droid, 0, 0)
#===================================================
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
    callObject.setPreCondition(droid, 0, 0)
    time.sleep(45)
    sim = callObject.getMainCard(droid)
    if SelLTE(sim) and CheckIMS(sim):
        smsNum = smsObject.getSmsNumber(droid, 0)
        SMS_ChangeDataCard(smsNum, 0)
    else:
        droid.log("not stay on LTE")
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
