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
            "cumCasesBySpecimenDate": "cumCasesBySpecimenDate",
            "hospitalCases": "hospitalCases"
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


def nation_cases_parse(nation_data : dict) -> list:
    #parse covid_api_nation_request

    days = nation_data['data']
    total_cases_over_week = 0
    total_hospital_cases_over_week =0
    total_deaths = 0
    cumCasesfound = False #flag to find the newest value
    final_data = []


    for i in range(len(days)):

        if(i>1 and i<8): #not interested in later data , dont look at the first day

        #TODO consider missing data
            day = days[i]
            total_cases_over_week+= int(day["newCasesByPublishDate"])
            total_hospital_cases_over_week += int(day["hospitalCases"])
            try :
                cum_death = int(day["cumCasesBySpecimenDate"])
            except TypeError : #Date has not yet been updated
                cum_death = False

            if( cum_death and (not cumCasesfound) ):
                cumCasesfound = True #unflag flag
                total_deaths = cum_death
        elif (i == 8):
            break


    return total_cases_over_week,total_hospital_cases_over_week,total_deaths



    return total_cases_over_week



def make_data_update(update_name : str) -> None:
    import global_variables
    #call combine_covid_api to get an update data
    update_content = combine_covid_API()

    print("I am called")
    json_content = dict()

    json_content['local_7day_infections'] = update_content[0]

    json_content['national_7day_infections'] = update_content[1]

    json_content['hospital_cases'] = update_content[2]

    json_content['deaths_total'] = update_content[3]



    for i in range (len(global_variables.UPDATES)):
        update = global_variables.UPDATES[i]
        if(update['title'] == update_name+"_scheduled"):
            global_variables.UPDATES[i] = {'title':update_name, 'content': json_content}


            for event in global_variables.SCHEDULED_EVENTS:
                if event.kwargs['update_name'] == update_name:
                    global_variables.SCHEDULED_EVENTS.remove(event)
            return

    global_variables.UPDATES.append( {'title' : update_name , 'content': json_content})



    return







def combine_covid_API() -> list:
    #call twice covid_api_request
    json_exeter_data = covid_API_request()
    json_england_data = json.loads(json.dumps(covid_API_request("england","nation")))
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
    week_rate_nation = nation_cases_parse(json_england_data)

    #combine the data into one array and return it

    final_data = []
    final_data.append(processed_exeter_data[0])
    final_data.extend(week_rate_nation)

    return final_data

def cancel_scheduled_update(update_name : str) -> None:
    import global_variables

    update_name = update_name.replace("_scheduled" , "")

    for event in global_variables.SCHEDULED_EVENTS:
        if event.kwargs['update_name'] == update_name:
            global_variables.SCHEDULER.cancel(event)
            global_variables.SCHEDULED_EVENTS.remove(event)

def config_schedule_updates(update_time : str ,update_name: str , repeated : bool) -> None:
    import global_variables
    #change time to a time_difference

    loc_time = time.asctime()
    loc_time = loc_time.split()
    simple_time = loc_time[3].split(":")

    scheduled_update_name = update_name + "_scheduled"

    scheduled_update_content = f"Update is planned at {update_time}"

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

    schedule_covid_updates(update_interval , update_name , repeated)
    return


def schedule_covid_updates(update_interval, update_name , repeated = False):
    '''Function uses the sched module to schedule updates to the covid data at the given time interval.'''
    import global_variables


    event = global_variables.SCHEDULER.enter(update_interval,0,make_data_update , kwargs= {'update_name' : update_name})

    global_variables.SCHEDULED_EVENTS.append(event)

    global_variables.SCHEDULER.run(blocking= False)




if __name__ == "__main__" :
    print("testing")
    data = parse_csv_data("nation_2021 -10-28.csv")
    assert len(data) == 639



    print(combine_covid_API())