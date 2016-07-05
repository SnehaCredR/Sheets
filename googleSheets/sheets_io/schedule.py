from apscheduler.schedulers.blocking import BlockingScheduler
import httplib2
import requests
def update_sheet():
    http=httplib2.HTTP()
    _, data = http.request("http://shelog.credr.io/sheets/index/")
    print "updated"


schedular = BlockingScheduler()
schedular.add_job(update_sheet, 'interval', seconds=60)
schedular.start()
