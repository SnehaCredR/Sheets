from apscheduler.schedulers.blocking import BlockingScheduler

def update_sheet():
    print "updated"

schedular = BlockingScheduler()
schedular.add_job(update_sheet, 'interval', seconds=3)
schedular.start()
