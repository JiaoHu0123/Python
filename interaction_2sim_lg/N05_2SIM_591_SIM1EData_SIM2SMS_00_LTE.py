#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-13

@author: panpan.wei
ScriptName:
Function:  (LTE)sim1  is main card and sim1  is data card, Sim1 ExchangeDataCard，Sim2 SMS
'''
import android
import ConfigParser  #get config file data
import os,sys  # use for path
import time   #use for time
import re # rename slog name

#define vars
caseTimeOut=200
config=ConfigParser.ConfigParser()
BASE_DIR=os.path.dirname(__file__)  #test scripts path name   #get parent path 
parent_dir=os.path.split(BASE_DIR)
Par_DIR=parent_dir[0]
Setting_path=os.path.join(Par_DIR,'Settings.ini')
config.readfp(open(Setting_path,'r'))
droid=android.Android(scriptname=__file__)
basic_path=os.path.abspath(Par_DIR)
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


passTimes=0
failTimes=0
phoneId=1  #0-sim1;1-sim2
testTimes=config.get("Setting", "Nw")  #get test times
hold_time=config.get("Setting","callHoldTime")
emcNum=config.get("CallNum", "emc")
website = config.get("BrowserAdd", "wapAddress")

droid.log("The test times is "+testTimes)
nwObject=net.NetWork(phoneId)
commObject=common.Common()
callObject=call.MMC(phoneId)
smsObject=sms.SMS(phoneId) 
psObject = ps.PS(scriptname = __file__)
print droid.log("parent path="+BASE_DIR)
print droid.log("parent_dir="+Par_DIR)
print droid.log(" =============================signal sim,open close sim card==========================")

sim = callObject.getMainCard(droid)
network = nwObject.getNetClass(droid, sim)
simtype = callObject.getSimType(droid, sim)
cardtype="DUAL"
droid.log("===sim="+sim+"===network="+network+"===simtype="+simtype)
version=droid.getCommandReturn("GetSoftwareVersion")
casename=droid.scriptname

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

defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)

if "LTE" in defaultMode:
    supportLTE=True
elif "AUTO" in defaultMode:
    droid.log("AUTO MODE")
else:
    supportLTE=False
droid.log("supportLTE="+str(supportLTE))

if network == "4G":
    networkok=True
else:
    nwObject.startSearchNet(droid, sim)
    network=nwObject.selLTE(droid, simtype)
    networkok=False

mode=commObject.getDutMode(droid)

if mode=="5M":
    defaultModeInt=nwObject.getModeStrToInt(defaultMode)
    if defaultModeInt!=18:
        droid.log("set to 5M")
        nwObject.setMode5M(droid)
        droid.log("wait 30s")
        time.sleep(30)
    else:
        droid.log("the mode is 5M")
elif mode=="4M":
    defaultModeInt=nwObject.getModeStrToInt(defaultMode)
    if defaultModeInt!=13:
        droid.log("set to W4M")
        nwObject.setModeW4M(droid)
    else:
        droid.log("the mode is W4M")
else:
    defaultModeInt=nwObject.getModeStrToInt(defaultMode)
    droid.log("the default mode int is "+str(defaultModeInt))
    
droid.log("parent path=" + BASE_DIR)
droid.log("parent_dir=" + Par_DIR)
droid.log("hold time=" + hold_time)


def SMS():
    Content=smsObject.getContent()
    smsNumber=smsObject.getSmsNumber(droid, 1)#sim1 send sms
    smsObject.setSMSSim(droid, 1)
    passFlag=smsObject.sendSMS(droid,smsNumber,Content)
    return passFlag

#close sim1 ,sim2 moc,open sim1
def ExchangeDataCard_SMS():
    global passTimes,failTimes
    callObject.setMainCard(droid, 0)
    time.sleep(40)
    callObject.setDataCard(droid, 0)
    time.sleep(30)
    for i in range(1,int(testTimes)+1):
        droid.log("This is the "+str(i)+" times test:")
        time.sleep(5)
        passFlag1= callObject.setDataCard(droid, 1)
        time.sleep(30)
        passFlag2 = SMS()
        time.sleep(20)
        passFlag3 = callObject.setDataCard(droid, 0)
        time.sleep(30)
        droid.log("===sms()="+str(passFlag2)+"====setDataCard="+str(passFlag1))
        if passFlag2 & passFlag1 & passFlag3:
            passTimes+=1
        else:
            failTimes+=1
        droid.log("=====================PASS: "+str(passTimes)+"; FAIL: "+str(failTimes))  
    callObject.setMainCard(droid, 0)
    time.sleep(40)
    callObject.setDataCard(droid, 0)
    time.sleep(30)
#============================================================================================================
droid.sendCommand("IsPluginSimCard 0","OK")
droid.sendCommand("IsPluginSimCard 1","OK")
if droid.sendCommand("IsPluginSimCard 0","OK") and droid.sendCommand("IsPluginSimCard 1","OK"):
        cardtype="DUAL"
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
        ExchangeDataCard_SMS()
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