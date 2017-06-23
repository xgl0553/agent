'''
Created on 

@author: admin
'''
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

import datetime

def my_job():
    print 'hello world' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S');

def my_job1(ss,ss1):
    print ss + '/' + ss1  + '->' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S');
    
if __name__ == "__main__":  
    sched = BlockingScheduler()
    trigger = IntervalTrigger(seconds=30)
    crontrigger = CronTrigger(minute='*/1')
    sched.add_job(my_job, trigger)
    sched.add_job(my_job1,crontrigger,['aaaa','bbbb'])
    sched.start()