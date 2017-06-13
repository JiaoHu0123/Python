#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-16

@author: zhaoxia.zhang
CaseName: SLAB_N05_Interaction_2SIM_1098_OpenCloseSim2_OpenCloseSim1Data_00
Fuction: 
    Main Card: Sim1 ,Data Card: Sim1
    OpenCloseSim2 + OpenCloseLTE: 1. Close Sim2, then main card change to Sim1 2. 2. Close LTE,wait a moment and open LTE 3. Set to default settings 4. loop step 1-3
'''
import android
import ConfigParser  # get config file data
import os, sys, time  # use for path
#================================================================================================
# define vars

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

time.sleep(10)

#==================================================================================================
caseTimeOut = 200
droid.setCaseTimeOut(caseTimeOut)

passTimes = 0
failTimes = 0
phoneId = 0  # 0-sim1;1-sim2
global testTimes

testTimes = config.get("Setting", "interaction")  # get test times
droid.log("The test times is " + testTimes)

callObject=call.MMC(scriptname = __file__)   # initial class
commObject = common.Common(scriptname = __file__)
nwObject = net.NetWork(scriptname = __file__)

version = droid.getCommandReturn("GetSoftwareVersion")
casename = droid.scriptname

global network, simtype, cardtype
sim = callObject.getMainCard(droid)
simtype = callObject.getSimType(droid, sim)
network = nwObject.getNetClass(droid, sim)
#==================================================================================
Status, ResultCause, SIM1Status, SIM2Status, Network1Status, Network2Status = nwObject.CheckCurrentSIMandNWStatus(droid, 2, "MULTI", "L+G", "NoVolte")
#  nwObject.CheckCurrentSIMandNWStatus(droid, expSimNum, expNWMode, expDualMode, expIMSStatus)
#  expNWMode, expDualMode
#  expSimNum={0,1,2}
#  expNWMode={LTE,WCDMA,TDSCDMA,GGE}
#  expIMSStatus={DualVolte,SingleVolte,NoVolte}

commObject.summary(droid, "INTERACTION", "MULTI", simtype, "Card Switch", "L+G", "120", SIM1Status, SIM2Status, Network1Status, Network2Status)

if "NA" in Status:
    droid.log("summary:NOT_SUPPORT")
    exit()
elif "Fail" in Status:
    droid.log("CriticalError: SIM Status ERROR or Network ERROR")
    exit()
else:
    droid.log("Sim Status Is Normal")
#============================================================================================================

time.sleep(5)
#===Network=====================================================================================================
print "#========================================================================="
defaultMode = droid.getCommandReturn("GetNetworkMode")
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

# mode=nwObject.getModeType(droid)

if "LTE" in defaultMode:
    supportLTE = True
else:
    supportLTE = False
droid.log("supportLTE=" + str(supportLTE))
#========================================================================================================

# function =================================================================================================

def OpenClose():
    # Close Sim2, then main card change to Sim1
    CloseSim2flag = nwObject.closeSim(droid, 1) 
    droid.log("Close Sim2, then main card change to Sim1")
    time.sleep(30)
    CloseLTEflag = nwObject.closeLte(droid) 
    droid.log("Close LTE")
    time.sleep(30)
    OpenLTEflag = nwObject.openLte(droid)  # Open LTE
    droid.log("Open LTE")
    time.sleep(30) 
    OpenSim2flag = nwObject.openSim(droid, 1)  # Open Sim2
    droid.log("Open Sim2")
    time.sleep(30)   
        
    droid.log("=CloseSim2flag=" + str(CloseSim2flag) + "=CloseLTEflag=" + str(CloseLTEflag) + "=OpenLTEflag=" + str(OpenLTEflag) + "=OpenSim2flag=" + str(OpenSim2flag))
    if CloseSim2flag and CloseLTEflag and OpenLTEflag and OpenSim2flag:
        droid.log("======OpenCloseSim2 + OpenCloselTE== pass=====")
        passflag = True
    else:
        droid.log("=======OpenCloseSim2 + OpenCloseLTE==FAIL======")
        passflag = False
        
    return passflag
         
def OpenCloseSim():
    global passTimes
    global failTimes
    for i in range(1, int(testTimes) + 1):
        droid.log("This is the " + str(i) + " times test:")
        # pre condicton:# set main card to Sim1 # set data card to Sim1
        callObject.setMainCard(droid, 0)  # set main card to Sim1
        time.sleep(30)
        callObject.setDataCard(droid, 0)  # set data card to Sim1
        time.sleep(30)
        passflag = OpenClose()
        # get sim1 and sim2 net state
        sim1Type = callObject.getSimType(droid, 0)
        sim2Type = callObject.getSimType(droid, 1)
        droid.log("sim1Type =" + sim1Type + "sim2Type=" + sim2Type)
        net1 = nwObject.getNetClass(droid, 0)
        net2 = nwObject.getNetClass(droid, 1)
        droid.log("sim1 network=" + net1 + "sim2 network=" + net2)
        if net1 == "UNKNOW":
            droid.log("card sim1 no service, wait 20s,check again")
            time.sleep(20)
            net1 = nwObject.getNetClass(droid, 0)
            droid.log("sim1 net=" + str(net1))
        elif net2 == "UNKNOW":
            droid.log("card sim2 no service, wait 20s,check again")
            time.sleep(20)
            net2 = nwObject.getNetClass(droid, 1)
            droid.log("sim2 net=" + str(net2))
        else:
            droid.log("have service")
        callObject.setMainCard(droid, 0)  # set main card back to Sim1
        time.sleep(30)
        callObject.setDataCard(droid, 0)  # set data card back to Sim1
        if passflag:
            passTimes += 1
        else:
            failTimes += 1
        
    time.sleep(30)
    droid.log("=====================PASS: " + str(passTimes) + "; FAIL: " + str(failTimes))
    callObject.setPreCondition(droid, 0, 0) 
    time.sleep(30)
    
#================================================================================================================
# check sim card
if droid.sendCommand("IsPluginSimCard 0", "OK") and droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "DUAL"
    droid.log("********************pluginSim two card=============================")   
    OpenCloseSim()
    
elif droid.sendCommand("IsPluginSimCard 0", "OK"):
    cardtype = "SINGLE1"
    droid.log("only one sim card1")
    simtype = callObject.getSimType(droid, 0)
    network = nwObject.getNetClass(droid, 0)
    droid.log("summary:NOT_SUPPORT")
    exit()
elif droid.sendCommand("IsPluginSimCard 1", "OK"):
    cardtype = "SINGLE2"
    droid.log("only one sim card2")
    simtype = callObject.getSimType(droid, 1)
    network = nwObject.getNetClass(droid, 1)
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
