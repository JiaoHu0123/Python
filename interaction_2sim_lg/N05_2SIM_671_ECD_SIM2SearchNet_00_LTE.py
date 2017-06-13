#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-10-13
@author: jiao.hu
ScriptName:SLAB_N05_Interaction_2SIM_671_ExchangeDataCard_SIM2SearchNet_00_LTE.py
Function:
dual simCard:Sim1 main card,Sim1 data card
1. datacard: Sim1->Sim2
2. Sim2 SearchNet
3. datacard: Sim2->Sim1
'''
import android
import ConfigParser  # get config file data
import os, sys  # use for path
import time  # use for time
import re  # rename slog name
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
from basic import call 
from basic import common
from basic import net
from time import sleep
import time
time.sleep(10)
caseTimeOut = 200

droid.setCaseTimeOut(caseTimeOut)
passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes
testTimes = config.get("Setting", "interaction")  # get interaction test times
callObject=call.MMC(scriptname = __file__)   # initial class
commObject = common.Common(scriptname = __file__)
nwObject = net.NetWork(scriptname = __file__)
version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname;
droid.log("The test times is " + testTimes)
time.sleep(5) 

global simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)
#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "LTE", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "INTERACTION", "LTE", simtype, "Data Switch", "L+G", "60", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================
# function ================================================================================================= 
def ChangeDataCard_SearchNet():  
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("The " + str(i) + " times test begin :")
        Flag1 = callObject.setDataCard(droid, 1)  # Select datacard sim2
        time.sleep(10)
        Flag2 = nwObject.searchingNet(droid, 1)  # Sim2 Search network
        droid.log("SIM2 Search network===pass")
        time.sleep(10)
        Flag3 = nwObject.searchingNet(droid, 0)  # MainCard1 Search network
        time.sleep(10)
        Flag4 = nwObject.selLTE(droid, 0)  # select MainCard1 to LTE Network  
        sleep(5)
        if Flag1 and Flag2 and Flag3 and Flag4:
            passTimes += 1
        else:
            failTimes += 1
        callObject.setDataCard(droid, 0)  # Select datacard sim1
        time.sleep(30)
    droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes)) 
        
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
    droid.log("********************pluginSim two card=============================")
    sim = callObject.getMainCard(droid)  # get maincard
    network = nwObject.getNetSate(droid, sim)  # get maincard net
    droid.log("network is" + network)
    simtype = callObject.getSimType(droid, sim)  # get maincard cardtype
    droid.log("simType is" + simtype)
    callObject.setDataCard(droid, 0)  # set Sim1 main card,Sim1 data card
    time.sleep(30)
    ChangeDataCard_SearchNet()
    time.sleep(30)
    callObject.setMainCard(droid, 0)
    time.sleep(30)
    callObject.setDataCard(droid, 0)  # set back to default state
    time.sleep(30)

elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    droid.log("only one sim card1")
    cardtype = "SINGLE1"
    network = nwObject.getNetClass(droid, 0)
    simtype = callObject.getSimType(droid, 0)
    droid.log("summary:NOT_SUPPORT")
    exit()

elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    droid.log("only one sim card2")
    cardtype = "SINGLE2"
    network = nwObject.getNetClass(droid, 1)
    simtype = callObject.getSimType(droid, 1)
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
