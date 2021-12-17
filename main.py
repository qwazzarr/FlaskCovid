import json
import logging
import os
from flask import render_template
from flask import Flask
from flask import request

from covid_data_handler import config_schedule_updates, make_data_update, cancel_scheduled_update
from covid_news_handling import update_news, config_news_update

app = Flask(__name__)


@app.route('/')
def program_start():
    """App route. Make 'Program started' log and redirect to /index"""
    logging.basicConfig(filename='sys.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
    logging.info("Program has been started")

    return index()


@app.route('/index')
def index():
    import global_variables

    global_variables.SCHEDULER.run(blocking=False)

    logging.basicConfig(filename='sys.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
    # look at request and get all parameters

    update_time = request.args.get('update')

    update_name = request.args.get('two')

    is_repeated = request.args.get('repeat')

    covid_update = request.args.get('covid-data')

    news_update = request.args.get('news')

    if covid_update:
        # schedule covid update
        logging.info("Covid update is scheduled")
        config_schedule_updates(update_time, update_name, is_repeated)

    if news_update:
        logging.info("News update is scheduled")
        with_covid = bool(covid_update)
        config_news_update(update_time, update_name, is_repeated, with_covid)

    update_deleted = request.args.get('update_item')
    if update_deleted:
        for update in global_variables.UPDATES:
            if update['title'] == update_deleted:
                logging.info(f"Update is deleted: {update_deleted}")
                global_variables.UPDATES.remove(update)
        if update_deleted == "INITIAL UPDATE":
            ready_update = False  # start to check whether any of old UPDATES remained. If not make another 'INITIAL
            # UPDATE'
            for update in global_variables.UPDATES:
                logging.warning("No updates are left. Making a new initial update")
                title = update['title']
                if not title.endswith("_scheduled"):
                    ready_update = True
            if not ready_update or len(
                    global_variables.UPDATES) == 0:  # case where no updates left - make another update
                make_data_update("INITIAL UPDATE")  # make a state as if programm hasnt started

        elif update_deleted.endswith("_scheduled"):
            cancel_scheduled_update(update_deleted)

    news_deleted = request.args.get('notif')
    if news_deleted:
        logging.info(f"News article is deleted : {news_deleted}")
        global_variables.DELETED_NEWS.add(news_deleted) # add news article to a hidden pool
        for news in global_variables.NEWS_ARTICLES:
            if news['title'] == news_deleted:
                global_variables.NEWS_ARTICLES.remove(news)

    if not (update_name or news_deleted or update_deleted or global_variables.HAS_BEEN_STARTED):
        global_variables.HAS_BEEN_STARTED = True

        # first time case
        make_data_update("INITIAL UPDATE")
        update_news()

    # get an access to global sets
    render_information = get_data_json()

    # render the page
    return render_template("index.html", **render_information)


def get_data_json() -> dict:
    """Function combine all needed data from global variables to one JSON"""
    import global_variables

    render_json = dict()

    render_json['news_articles'] = global_variables.NEWS_ARTICLES
    render_json['updates'] = global_variables.UPDATES

    for update in reversed(global_variables.UPDATES):
        if type(update['content']) is dict:
            most_recent_update = update
            break

    render_json['title'] = most_recent_update['title']

    render_json['location'] = 'Exeter'

    render_json['nation_location'] = 'England'
    render_json['image'] = 'favicon.ico'
    render_json['favicon'] = 'favicon.ico'

    last_content = most_recent_update['content']
    render_json.update(last_content)

    return render_json
if __name__ == '__main__':
    with open("config.json", "r") as f:
        CONFIG = json.load(f)

    logging.getLogger('werkzeug').disabled = True

    DEBUG = CONFIG['debug']
    app.run(debug=DEBUG)
