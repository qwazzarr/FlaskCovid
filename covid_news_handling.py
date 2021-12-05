import requests
import json

import time



def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    '''Access current news data using the requests module and the News API (https://newsapi.org/)'''
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
    print(complete_url)

    response = requests.get(complete_url)
    json_response = response.json()

    print(json_response)

    return json_response


def update_news(update_name :str = "default" , with_covid : bool = False) -> None:
    '''Function uses the news API request within the function and
    is able to update a data structure containing news articles'''
    import global_variables


    most_recent_ten = []
    full_json = news_API_request()
    articles = full_json["articles"]
    for article in articles:
        if(article["title"] in global_variables.DELETED_NEWS):
            continue
        new_news= dict()
        content =article['description'] +"\n"+article['url']
        new_news['title'] = article['title']
        new_news['content'] = content
        most_recent_ten.append(new_news)
        if (len(most_recent_ten) == 10):
            break


    if (not with_covid):
        for update_i in range (len(global_variables.UPDATES)):
            update = global_variables.UPDATES[update_i]
            if (update['title'] == update_name+"_scheduled"):
                global_variables.UPDATES[update_i] = {'title':update_name , 'content' : 'News has been updated.'}
    global_variables.NEWS_ARTICLES = (most_recent_ten)
    return




def schedule_news_updates(update_interval, update_name, repeated , with_covid : bool) -> None:

    import global_variables

    event = global_variables.SCHEDULER.enter(update_interval,  1, update_news, kwargs={'update_name': update_name , 'with_covid':with_covid})

    global_variables.SCHEDULED_EVENTS.append(event)

    global_variables.SCHEDULER.run(blocking=False)


def config_news_update(update_time : str ,update_name: str , repeated : bool , with_covid : bool) -> None:

    import global_variables
    #change time to a time_difference

    loc_time = time.asctime()
    loc_time = loc_time.split()
    simple_time = loc_time[3].split(":")


    if(not with_covid):
        scheduled_update_name = update_name + "_scheduled"

        scheduled_update_content = f"News update is planned at {update_time}"

        global_variables.UPDATES.append({"title": scheduled_update_name, "content": scheduled_update_content})



    guessed_time = update_time.split(":")


    hours, minutes, seconds = int(simple_time[0]), int(simple_time[1]), int(simple_time[2])
    ghours, gminutes = int(guessed_time[0]), int(guessed_time[1])

    if (ghours > hours):

        if (gminutes < minutes):
            gminutes += 60
            ghours -= 1
    elif (ghours == hours):

        print("lel")
        if (gminutes < minutes):
            ghours += 23
            gminutes += 60

        elif (minutes == gminutes):
            seconds = 0
    elif (ghours < hours):
        print("lel1")
        ghours += 24

        if (gminutes < minutes):
            ghours -= 1
            gminutes += 60


    update_interval = (3600 * (ghours - hours) + 60 * (gminutes - minutes) - seconds)


    print(update_interval)
    #log that new update is getting processed

    schedule_news_updates(update_interval , update_name , repeated , with_covid)

    return



if __name__ == "__main__":
    update_news()
