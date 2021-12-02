import json

from uk_covid19 import Cov19API
from main import UPDATES , NEWS_ARTICLES, DELETED_NEWS

import sched
import time



def parse_csv_data(filename_csv):
    '''Function takes    an argument called csv filename and returns a list of strings for the rows in the file.'''
    with open(filename_csv,"r") as file:
        list_of_lines= file.readlines()
        return list_of_lines

def process_covid_csv_data(covid_csv_data):
    '''Function takes a list of data from an argument called covid csv data,
    and returns three variables; the number of cases in the last 7 days,
    the current number of hospital cases and the cumulative number of deaths, as contained in the given csv file.'''

    last_7_days_cases = 0 #inititate variables
    total_hospitalised = 0
    total_deaths = 0
    deaths_updated = False #flags to find the newest data
    current_hospitalised_updated = False
    for i in range(1,len(covid_csv_data)): #skip names of columns
        day = covid_csv_data[i]
        day = day.split(",")

        if (i >2 and i < 10): # ignore first and second day that are incomplete
            day_cases =  int(day[-1])

            last_7_days_cases+=day_cases

        try:
            day_hospitalised = int(day[5])
        except ValueError: #No data for this day
            day_hospitalised = False

        if(day_hospitalised and (not current_hospitalised_updated)):
            current_hospitalised_updated = True #unflag flag
            total_hospitalised = day_hospitalised

        try :
            cum_death = int(day[4])
        except ValueError : #Date has not yet been updated
            cum_death = False

        if( cum_death and (not deaths_updated)  ):
            deaths_updated = True #unflag flag
            total_deaths = cum_death

        if(i >= 10 and deaths_updated and current_hospitalised_updated): # check whether all information has been found
            break

    return last_7_days_cases,total_hospitalised,total_deaths


def covid_API_request(location = "Exeter", location_type = "ltla"):
    ''' Function accesses current COVID-19 data using
    the uk-covid-19 module provided by Public Health England.
    Then it returns up-to-date Covid data as a dictionary.'''
    #areaType=nation;areaName=england for nation
    filters = [
        f'areaType={location_type}',
        f'areaName={location}'
    ] # set filters
    if(location_type == "nation"):
        cases_and_deaths = {
            "areaName":"areaName",
            "date":"date",
            "newCasesByPublishDate" : "newCasesByPublishDate",
        }
    else:
        cases_and_deaths = {
            "areaCode": "areaCode",
            "areaName": "areaName",
            "areaType" : "areaType",
            "date": "date",
            "cumDailyNsoDeathsByDeathDate":"cumDailyNsoDeathsByDeathDate",
            "hospitalCases" : "hospitalCases",
            "newCasesBySpecimenDate":"newCasesBySpecimenDate"

        } # set structure of the data

    api = Cov19API(filters=filters, structure=cases_and_deaths)

    data = api.get_json() # access data


    return data


def nation_cases_parse(nation_data :str) -> int:
    #parse covid_api_nation_request

    days = nation_data['data']
    total_cases_over_week = 0
    for i in range(len(days)):

        if(i>6): #not interested in later data , dont c
            break
        #TODO consider missing data
        total_cases_over_week += days[i]["newCasesByPublishDate"]
    return total_cases_over_week



def make_data_update(update_name):
    global UPDATES
    #call combine_covid_api to get an update data
    update_content = combine_covid_API()

    UPDATES.add({'title':update_name, 'content': update_content})







def combine_covid_API() -> list:
    #call twice covid_api_request
    json_exeter_data = covid_API_request()
    json_england_data = covid_API_request("england","nation")

    #change data so it can apply to covid_csv_data
    exeter_csv_data = []
    for day in json_exeter_data['data']:

        line_of_values =""
        day_values = day.values()

        for value in (day_values):
            if (value is None):
                value =""
            line_of_values+= str(value) +","
        exeter_csv_data.append(line_of_values[:-1]) #get rid of the last ','
    #use process covid_csv_data for a first one

    processed_exeter_data = process_covid_csv_data(exeter_csv_data)

    #use nation_cases_parse to parse nation data
    week_rate_nation = nation_cases_parse(processed_exeter_data)

    #combine the data into one array and return it

    final_data = processed_exeter_data.append(week_rate_nation)

    return final_data

def config_schedule_updates(time,update_name):
    #change time to update_interval , calls schedule_covid_updates
    pass

def schedule_covid_updates(update_interval, update_name):
    '''Function uses the sched module to schedule updates to the covid data at the given time interval.'''
    s = sched.scheduler(time.time, time.sleep)
    s.enter(update_interval,action=make_data_update(update_name))
    s.run(blocking=False)


    pass




if __name__ == "__main__" :
    print("testing")
    data = parse_csv_data("nation_2021 -10-28.csv")
    assert len(data) == 639

    print(covid_API_request("england","nation"))

    combine_covid_API()