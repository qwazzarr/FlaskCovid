
global DELETED_NEWS , NEWS_ARTICLES , HAS_BEEN_STARTED , UPDATES , SCHEDULED_EVENTS

import sched
import time

UPDATES = []
NEWS_ARTICLES = []
HAS_BEEN_STARTED = False
DELETED_NEWS = set()


SCHEDULED_EVENTS =[]


SCHEDULER = sched.scheduler(time.time, time.sleep)
