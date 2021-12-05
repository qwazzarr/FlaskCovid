
import time

import sched


scheduler = sched.scheduler(time.time, time.sleep)

def hello(string : str):

    print("HELLo " + string)

event = scheduler.enter(2,0, hello, kwargs={'string':"jui"})


event.kw


