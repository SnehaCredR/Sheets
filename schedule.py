#!/usr/bin/python2 

from apscheduler.schedulers.blocking import BlockingScheduler
import httplib2
import logging

# import requests
def update_sheet():
    http=httplib2.Http()
    print "Starting loop"    
    _, data = http.request("http://shelog.credr.io/sheets/index/")

if __name__ == '__main__':
    logging.basicConfig()
    schedular = BlockingScheduler()
    schedular.add_job(update_sheet, 'interval', hour="0")
    schedular.start()
