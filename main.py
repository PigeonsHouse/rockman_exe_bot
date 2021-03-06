from functions.streamings import LTLlisten
from functions.schedules import scheduler
import time
from datetime import datetime
import threading
from utils.clients import client

if __name__ == '__main__':
    threading.Thread(target = LTLlisten, args=(client,)).start()
    print("start streaming timeline")

    all_jobs = scheduler.get_jobs()

    print("start schedule preparation")
    while True:
        try:
            scheduler.run_pending()
            time.sleep(5)
        except Exception as e:
            print(datetime.now())
            print(e)
            print('\n')
