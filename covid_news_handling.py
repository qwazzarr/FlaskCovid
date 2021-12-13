import requests
import json

import time


def news_API_request(covid_terms : str ="Covid COVID-19 coronavirus"):
    """
    Access current news data using the requests module and the News API (https://newsapi.org/)
    :param str covid: String of keywords divided with spaces.

    """
    import logging
    logging.basicConfig(filename='sys.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    with open("config.json", "r") as f:
        config = json.load(f)

    covid_terms = covid_terms.split()

    api_text = ""
    for i in range(len(covid_terms)):
        if (i == len(covid_terms) - 1):
            api_text += covid_terms[i]
            break
        api_text += covid_terms[i] + " OR "

    complete_url = f"https://newsapi.org/v2/everything?q={api_text}&sortBy=publishedAt&language=en&apiKey={config['news_api']}"
    try:
        response = requests.get(complete_url)

        if response.status_code == 404:
            logging.critical("Api adress is not found")
            raise Exception("Api address is not found")
        elif response.status_code == 401:
            logging.critical("Api key is invalid")
            raise Exception("Api key is invalid")
        elif response.status_code == 500:
            logging.critical("News API server error")
            raise Exception("News API server error")
        json_response = response.json()
    except Exception as e:

        logging.critical("News API request was not successful")

    return json_response


def update_news(update_name: str = "default", with_covid: bool = False) -> None:
    """Function uses the news API request within the function and
     update global variable NEWS_ARTICLES containing news articles
     :param str update_name: The name of the future update
     :param bool with_covid: Bool value , that shows whether this Update is being considered
     by covid_data_handler module or not."""
    import global_variables

    most_recent_ten = []
    full_json = news_API_request()

    if(full_json['status'] != 'ok'): #check if a request was successful
        return

    articles = full_json["articles"]
    for article in articles:
        if (article["title"] in global_variables.DELETED_NEWS):
            continue
        new_news = dict()
        content = article['description'] + "\n" + article['url']
        new_news['title'] = article['title']
        new_news['content'] = content
        most_recent_ten.append(new_news)
        if (len(most_recent_ten) == 10):
            break

    if (not with_covid):
        for update_i in range(len(global_variables.UPDATES)):
            update = global_variables.UPDATES[update_i]
            if (update['title'] == update_name + "_scheduled"):
                global_variables.UPDATES[update_i] = {'title': update_name, 'content': 'News has been updated.'}
    global_variables.NEWS_ARTICLES = (most_recent_ten)
    return


def schedule_news_updates(update_interval : int , update_name : str, repeated : str, with_covid: bool) -> None:
    """Function uses the sched module to schedule updates to the news_data at the given time interval. It appends events
       to global variable SCHEDULED_EVENTS. For repeated functions it schedule a recursive in 24h interval with the same
        parameters. Function is used only for the case when there is no covid_updates scheduled

        :param int update_interval: seconds until the update
        :param str update_name: the name of the update
        :param str repeated: string that will be empty in case of not-repeated update
        :param bool with_covid: Bool value , that shows whether this Update is being considered
            by covid_data_handler module or not"""
    import global_variables

    event = global_variables.SCHEDULER.enter(update_interval, 1, update_news,
                                             kwargs={'update_name': update_name, 'with_covid': with_covid})

    if (repeated):
        event_2 = global_variables.SCHEDULER.enter(update_interval + 86400, 0, schedule_news_updates,
                                                   kwargs={'update_interval': update_interval,
                                                           'update_name': update_name, 'repeated': repeated})
        global_variables.SCHEDULED_EVENTS.append(event_2)

    global_variables.SCHEDULED_EVENTS.append(event)

    global_variables.SCHEDULER.run(blocking=False)


def config_news_update(update_time: str, update_name: str, repeated: str, with_covid: bool) -> None:
    """Function uses update_time in format 'Hours:Minutes' to calculate a time difference in seconds.Also it consider
     missing data for update_time and assumes it as an instant update. Then it calls schedule_news_updates. Function is
     not reponsible for updating global variable UPDATES except for the case when covid updates are not needed

     :param str update_time: time in a format (HH:MM) for a scheduled update
     :param str update_name: a name for the update
     :param bool with_covid: Bool value , that shows whether this Update is being considered
            by covid_data_handler module or not """
    import global_variables
    # change time to a time_difference

    loc_time = time.asctime()
    loc_time = loc_time.split()
    simple_time = loc_time[3].split(":")

    if (not with_covid):
        scheduled_update_name = update_name + "_scheduled"

        scheduled_update_content = f"News update is planned at {update_time}"

        global_variables.UPDATES.append({"title": scheduled_update_name, "content": scheduled_update_content})

    if (update_time == ''):
        guessed_time = simple_time
    else:
        guessed_time = update_time.split(":")

    hours, minutes, seconds = int(simple_time[0]), int(simple_time[1]), int(simple_time[2])
    ghours, gminutes = int(guessed_time[0]), int(guessed_time[1])

    if ghours > hours:

        if gminutes < minutes:
            gminutes += 60
            ghours -= 1
    elif ghours == hours:

        if gminutes < minutes:
            ghours += 23
            gminutes += 60

        elif minutes == gminutes:
            seconds = 0
    elif ghours < hours:
        ghours += 24

        if gminutes < minutes:
            ghours -= 1
            gminutes += 60

    update_interval = (3600 * (ghours - hours) + 60 * (gminutes - minutes) - seconds)


    schedule_news_updates(update_interval, update_name, repeated, with_covid)

    return


if __name__ == "__main__":
    update_news()
