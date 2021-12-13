"""
This module contains global variables and acts as a database. Main idea for its creation
was to get rid of circular import error without a huge refactoring.
"""
global DELETED_NEWS, NEWS_ARTICLES, HAS_BEEN_STARTED, UPDATES, SCHEDULED_EVENTS

import sched
import time

UPDATES = []
NEWS_ARTICLES = []
HAS_BEEN_STARTED = False
DELETED_NEWS = set()

SCHEDULED_EVENTS = []

SCHEDULER = sched.scheduler(time.time, time.sleep)
