from functions.streamings import LTLlisten
from functions.schedules import scheduler
import time
import threading

if __name__ == '__main__':
    threading.Thread(target = LTLlisten).start()

    while True:
        try:
            scheduler.run_pending()
            time.sleep(5)
        except Exception as e:
            print(e)