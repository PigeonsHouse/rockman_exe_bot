from functions.streamings import LTLlisten
from functions.schedules import scheduler
import time
import threading
from utils.clients import client

if __name__ == '__main__':
    threading.Thread(target = LTLlisten, args=(client,)).start()

    all_jobs = scheduler.get_jobs()

    while True:
        try:
            scheduler.run_pending()
            time.sleep(5)
        except Exception as e:
            print(e)