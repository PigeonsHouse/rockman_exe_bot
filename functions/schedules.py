from utils.load_yaml import config_dict
from .functions import chime, task_boost, random_toot, day_change, summer_target, spring_target
import schedule

scheduler = schedule.Scheduler()

for i, task_time in enumerate(config_dict['time']['chimetime']):
    scheduler.every().day.at(task_time).do(chime, chime_time=task_time, class_time=(i + 1 if i < 5 else None))
for task_time in config_dict['time']['tasktime']:
    scheduler.every().day.at(task_time).do(task_boost)
for task_time in config_dict['time']['rndtime']:
    scheduler.every().day.at(task_time).do(random_toot)
scheduler.every().day.at("00:00").do(day_change)
scheduler.every().sunday.at("09:00").do(summer_target)
scheduler.every().wednesday.at("21:00").do(summer_target)
scheduler.every().sunday.at("09:00").do(spring_target)
scheduler.every().wednesday.at("21:00").do(spring_target)
