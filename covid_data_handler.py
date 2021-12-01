import json

from uk_covid19 import Cov19API
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






    pass

def covid_API_request(location = "Exeter", location_type = "ltla"):
    ''' Function accesses current COVID-19 data using
    the uk-covid-19 module provided by Public Health England.
    Then it returns up-to-date Covid data as a dictionary.'''
    filters = [
        f'areaType={location_type}',
        f'areaName={location}'
    ] # set filters
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


def schedule_covid_updates(update_interval, update_name):
    '''Function uses the sched module to schedule updates to the covid data at the given time interval.'''
    s = sched.scheduler(time.time, time.sleep)
    covid_update = s.enter(update_interval,action=covid_API_request())
    pass


if __name__ == "__main__" :
    print("testing")
    data = parse_csv_data("nation_2021 -10-28.csv")
    assert len(data) == 639

    a , b , c = process_covid_csv_data(parse_csv_data("nation_2021 -10-28.csv"))
    assert a == 240_299
    assert b == 7_019
    assert c == 141_544

    covid_API_request()