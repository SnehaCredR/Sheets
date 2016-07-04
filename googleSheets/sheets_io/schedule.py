from apscheduler.schedulers.blocking import BlockingScheduler
import httplib2
import requests
def update_sheet():
    http=httplib2.HTTP()
    _, data = http.request("")
    print "updated"

schedular = BlockingScheduler()
schedular.add_job(update_sheet, 'interval', hours=12)
schedular.start()
