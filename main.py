from flask import render_template
from flask import Flask
from flask import request
import time
import sched
import requests
import json
import logging
from uk_covid19 import Cov19API

s = sched.scheduler(time.time, time.sleep)
app = Flask(__name__)
DELETED_NEWS = set()

UPDATES = []
NEWS_ARTICLES = []


@app.route('/')
def program_start():
    logging.basicConfig(filename='sys.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.warning('Program started')
    return main()



@app.route('/index')
def index():
    s.run(blocking=False)
    global DELETED_NEWS
    global UPDATES
    #look at request and get all parameters
    update_time = request.args.get('update')
    update_name = request.args.get('two')


    is_repeated = request.args.get('repeat')


    covid_update = request.args.get('covid-data')


    news_update = request.args.get('news')




    update_deleted = request.args.get('update_item')
    for update in UPDATES:
        if update['title'] == update_deleted:
            UPDATES.remove(update)



    news_deleted = request.args.get('notif')
    DELETED_NEWS.add(news_deleted)


    #schedule all updates based on parameters

    #get an access to global sets


    #render the page
    return main()

@app.route('/main')
def main():
    s.run(blocking= False)








    return render_template("index.html",)


def get_data_json():
    updates = UPDATES
    news = NEWS_ARTICLES
    json = dict()
    if (len(UPDATES) == 0):#consider base cases
        json['updates'] = [{'title': "None", 'content': "No updates has been scheduled"}]
        json['news'] = [{'title': "None", 'content': 'No updates has been scheduled'}]
    most_recent_update = updates[-1]
    json['title'] = most_recent_update['title']
    