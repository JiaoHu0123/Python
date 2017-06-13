#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2016-8-18

@author: songchao.chu
ScriptName:SLAB_N05_Interaction_2SIM_DS_435_Sim1OpenCloseData_Sim2 SMS_00_IMS.py
Function:  MainCard:SIM1&DataCard:SIM1
           Sim1OpenCloseData and Sim2 SMS (IMS)
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
droid.setCaseTimeOut(caseTimeOut)


passTimes=0
failTimes=0
phoneId=1  #0-sim1;1-sim2
testTimes=config.get("Setting", "interaction")  #get test times
hold_time=config.get("Setting","callHoldTime")
emcNum=config.get("CallNum", "emc")

droid.log("The test times is "+testTimes)
nwObject=net.NetWork(phoneId)
commObject=common.Common()
callObject=call.MMC(phoneId)
smsObject=sms.SMS(phoneId) 
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

droid.log("parent path=" + BASE_DIR)
droid.log("parent_dir=" + Par_DIR)
droid.log("hold time=" + hold_time)

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

defaultMode = droid.getCommandReturn("GetNetworkMode")
droid.log("===================defualtMode=" + defaultMode)
#check whether supportLTE
if "LTE" in defaultMode:
    supportLTE=True
elif "AUTO" in defaultMode:
    droid.log("AUTO MODE")
else:
    supportLTE=False
droid.log("supportLTE="+str(supportLTE))

# check whether supported volte
if nwObject.checkVolte(droid, sim):
    supportVolte = True
else:
    supportVolte = False
    droid.log("summary:NOT_SUPPORT") 
    exit() 
droid.log("supportVolte=" + str(supportVolte))
#============================================================================================================
def CloseData(sim):
    if nwObject.closeData(droid, sim):
        droid.log("====================step2: close data,and wait 10s")
        time.sleep(10)
        closeFlag=True
    else:
        closeFlag=False
    return closeFlag 
def OpenData(sim):
    if nwObject.openData(droid,sim):
        droid.log("====================step2: open data,and wait 30s")
        time.sleep(30)
        openFlag=True
    else:
        openFlag=False
    return openFlag

def SMS():
    Content=smsObject.getContent()
    smsNumber=smsObject.getSmsNumber(droid, 1)#sim2 send sms
    smsObject.setSMSSim(droid, 1)
    passFlag=smsObject.sendSMS(droid,smsNumber,Content)
    return passFlag

#close sim1 ,sim2 moc,open sim1
def OpenCloseData_SMS():
    global passTimes,failTimes
    callObject.setPreCondition(droid, 0, 0)
    for i in range(1,int(testTimes)+1):
        droid.log("This is the "+str(i)+" times test:")
        droid.log("==================step1:  close data"+str(1)+",and wait 5s")
        time.sleep(5)
        passFlag1=CloseData(0)
        smsFlag= sms()
        time.sleep(20)
        passFlag2=OpenData(0)
#         passFlag4= callObject.voiceCall(droid, callNumber, hold_time)
        time.sleep(10)
        droid.log("===CloseData(1)="+str(passFlag1)+"===OpenData(1)="+str(passFlag2)+"===sms(2)="+str(smsFlag))
        if passFlag1&smsFlag&passFlag2:
            passTimes+=1
        else:
            failTimes+=1
        droid.log("=====================PASS: "+str(passTimes)+"; FAIL: "+str(failTimes))  
        callObject.setPreCondition(droid, 0, 0)
    

#============================================================================================================
droid.sendCommand("IsPluginSimCard 0","OK")
droid.sendCommand("IsPluginSimCard 1","OK")
net = nwObject.getNetClass(droid,sim)
simtype=callObject.getSimType(droid, sim)
volteFlag = nwObject.checkVolte(droid, sim)
if droid.sendCommand("IsPluginSimCard 0","OK") and droid.sendCommand("IsPluginSimCard 1","OK"):
    cardtype="DUAL"
    droid.log("************************************pluginSim two card=================================") 
    if net == "4G" and volteFlag:
        OpenCloseData_SMS()
    elif supportLTE:
         nwObject.startSearchNet(droid,sim)
         nwObject.selLTE(droid,simtype) 
         OpenCloseData_SMS() 
    else:
        droid.log("summary:NOT_SUPPORT") 
        exit()    
          
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