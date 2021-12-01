import requests
import json


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


def update_news():
    '''Function uses the news API request within the function and
    is able to update a data structure containing news articles'''
    global DELETED_NEWS
    most_recent_ten = []
    full_json = news_API_request()
    articles = full_json["articles"]
    for article in articles:
        if(article["title"] in DELETED_NEWS):
            continue
        most_recent_ten.append([article["title"], article["url"]])
        if (len(most_recent_ten) == 10):
            break
    print(most_recent_ten)
    return most_recent_ten


if __name__ == "__main__":
    update_news()
