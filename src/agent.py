# -*- coding:utf-8 -*-

#import logging
import logging.handlers

import psutil  
import datetime  

import platform
import ConfigParser

import urllib
import urllib2
import json

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
#print u"CPU  %s"%psutil.cpu_count()  
#print u"logical CPU个数 %s"%psutil.cpu_count(logical=False)  
#print u"CPU uptimes"  
#print psutil.cpu_times()  
#print ""  

#req = urllib2.Request(server,test_data_urlencode)
#res_data = urllib2.urlopen(req)
#res = res_data.read()
#print res

#print(platform.architecture())

#print(platform.platform())

#print(platform.system())
 
 
#print(platform.python_version())

# cpu使用率
#print psutil.cpu_percent(interval=1)

#print "disk" 
#print psutil.disk_partitions()

# Windows or Linux
#sysstr = platform.system()
#print(sysstr)

 #data='{"uuid":"' + uuid + '","type":"cpu",' + '"value":"' + "555555" + '"}'
    #test_data_urlencode = urllib.urlencode(test_data) 
    #print data
    #test_data_urlencode = urllib.urlencode(json.loads(data))


    

#for disk in psutil.disk_partitions(False):
#    if(sysstr == 'Windows' and  disk.fstype != ''):
#        print disk.device
#        print psutil.disk_usage(disk.mountpoint)
        
#if(sysstr == 'Linux'):
#    for disk in psutil.disk_partitions():
#        print disk.mountpoint
#        print psutil.disk_usage(disk.mountpoint)
#


#print u"系统启动时间 %s"%datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")  

#print psutil.users()
   
#users_count = len(psutil.users())  
#users_list = ",".join([ u.name for u in psutil.users()])  
#print u"当前有%s个用户，分别是%s"%(users_count, users_list)  
  
#net = psutil.net_io_counters()  
#bytes_sent = '{0:.2f} kb'.format(net.bytes_recv / 1024)  
#bytes_rcvd = '{0:.2f} kb'.format(net.bytes_sent / 1024)  
#print u"网卡接收流量 %s 网卡发送流量 %s"%(bytes_rcvd, bytes_sent)  

logger = logging.getLogger("root")
logger.setLevel(logging.ERROR)
filehandler=logging.handlers.TimedRotatingFileHandler("../logs/agent.log",'D',1,0)
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(message)s')
filehandler.setFormatter(formatter) 
filehandler.suffix="%Y%m%d.log"
logger.addHandler(filehandler)

def sendCPUInfo(uuid,server):
    try:
        cpuData = {}
        cpuData['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cpuData['uuid'] = uuid
        cpuData['type'] ='cpu'
        cpuData['value'] = psutil.cpu_percent(interval=1)
        print cpuData
        data = urllib.urlencode(cpuData)
        req = urllib2.Request(server,data)
        res_data = urllib2.urlopen(req)
        res_data.read()
        
    except:
        logger.exception("Exception in sendCPUInfo ")
        
    
def sendMEMInfo(uuid,server):
    try:
        mem = psutil.virtual_memory()
        meminfo ={}
        meminfo['total'] = mem.total
        meminfo['available'] = mem.available
        meminfo['percent'] = mem.percent
        meminfo['used'] = mem.used
        meminfo['free'] = mem.free
    
        memData ={}
        memData['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        memData['uuid'] = uuid
        memData['type'] = 'mem'
        memData['value'] = json.dumps(meminfo)
        data = urllib.urlencode(memData)
        req = urllib2.Request(server,data)
        res_data = urllib2.urlopen(req)
        res_data.read()
        print memData
    except:
        logger.exception("Exception in sendMEMInfo ")

def sendDiskInfo(uuid,server):
    try:
        sysstr = platform.system()
        diskinfo=[]
        if(sysstr == 'Windows'):
            for disk in psutil.disk_partitions(False):
                if disk.fstype != '':
                    info={}
                    info['mountpoint'] = disk.mountpoint
                    disk_usage = psutil.disk_usage(disk.mountpoint)
                    info['total'] = disk_usage.total
                    info['used'] = disk_usage.used
                    info['free'] = disk_usage.free
                    info['percent'] = disk_usage.percent
                    diskinfo.append(info)
        elif sysstr == 'Linux':
            for disk in psutil.disk_partitions(False):
                info={}
                info['mountpoint'] = disk.mountpoint
                disk_usage = psutil.disk_usage(disk.mountpoint)
                info['total'] = disk_usage.total
                info['used'] = disk_usage.used
                info['free'] = disk_usage.free
                info['percent'] = disk_usage.percent
                diskinfo.append(info)
                
        diskData ={}
        diskData['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        diskData['uuid'] = uuid
        diskData['type'] = 'disk'
        diskData['value'] = json.dumps(diskinfo)
        
        data = urllib.urlencode(diskData)
        req = urllib2.Request(server,data)
        res_data = urllib2.urlopen(req)
        res_data.read()
                
        print diskData
    except:
        logger.exception("Exception in sendDiskInfo ")

if __name__ == "__main__":
    
    cp = ConfigParser.SafeConfigParser()
    cp.read('../conf/agent.conf')
    uuid = cp.get('default', 'uuid')
    server = cp.get('default','server')
    
    logger.info(uuid)
    logger.info(server)
    
    sched = BlockingScheduler()
    trigger = IntervalTrigger(seconds=30)
    crontrigger = CronTrigger(minute='*/1')
    sched.add_job(sendCPUInfo, trigger,[uuid,server])
    sched.add_job(sendMEMInfo,crontrigger,[uuid,server])
    sched.add_job(sendDiskInfo,crontrigger,[uuid,server])
    sched.start()
    