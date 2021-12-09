from flask import render_template, url_for
from flask import Flask
from flask import request
import time
import sched
import requests
import json
import logging
from uk_covid19 import Cov19API




from covid_data_handler import config_schedule_updates , make_data_update , cancel_scheduled_update
from covid_news_handling import update_news ,config_news_update



app = Flask(__name__)



@app.route('/')
def program_start():
    logging.basicConfig(filename='sys.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.warning('Program started')
    return index()



@app.route('/index')
def index():
    import global_variables

    global_variables.SCHEDULER.run(blocking= False)



    #look at request and get all parameters

    update_time = request.args.get('update')

    update_name = request.args.get('two')


    is_repeated = request.args.get('repeat')


    covid_update = request.args.get('covid-data')


    news_update = request.args.get('news')


    if(covid_update):
        #schedule covid update
        config_schedule_updates(update_time,update_name,is_repeated)


    if(news_update):
        if(covid_update):
            with_covid = True
        else:
            with_covid = False
        config_news_update(update_time, update_name , is_repeated , with_covid)


    update_deleted = request.args.get('update_item')
    if(update_deleted):
        for update in global_variables.UPDATES:
            if update['title'] == update_deleted:
                global_variables.UPDATES.remove(update)
        if(update_deleted == "INITIAL UPDATE"):

            ready_update = False # start to check whether any of old UPDATES remained. If not make another 'INITIAL UPDATE'
            for update in global_variables.UPDATES:
                title = update['title']
                if not title.endswith("_scheduled"):
                    ready_update = True
            if not ready_update or len(global_variables.UPDATES == 0): #case where no updates left - make another update
                make_data_update("INITIAL UPDATE") # make a state as if programm hasnt started



        elif(update_deleted.endswith("_scheduled")):
            cancel_scheduled_update(update_deleted)




    news_deleted = request.args.get('notif')
    if(news_deleted):
        global_variables.DELETED_NEWS.add(news_deleted)
        for news in global_variables.NEWS_ARTICLES:
            if news['title'] == news_deleted:
                global_variables.NEWS_ARTICLES.remove(news)

    if(not (update_name or news_deleted or update_deleted or global_variables.HAS_BEEN_STARTED ) ):


        global_variables.HAS_BEEN_STARTED = True


        #first time case
        make_data_update("INITIAL UPDATE")
        update_news()

    #

    #get an access to global sets
    render_information = get_data_json()


    #render the page
    return render_template("index.html",**render_information)


def get_data_json() -> dict:
    import global_variables

    json = dict()

    json['news_articles'] =   global_variables.NEWS_ARTICLES
    json['updates'] = global_variables.UPDATES

    for update in reversed(global_variables.UPDATES):
        if(type(update['content']) == type(dict())):
            most_recent_update = update
            break


    json['title'] = most_recent_update['title']

    json['location'] = 'Exeter'

    json['nation_location'] = 'England'
    json['image'] = 'favicon.ico'
    json['favicon'] = 'favicon.ico'

    last_content = most_recent_update['content']
    json.update(last_content)

    return json

if __name__ == '__main__':
    with open("config.json", "r") as f:
        config = json.load(f)
    debug = config['debug']
    app.run(debug = debug)
