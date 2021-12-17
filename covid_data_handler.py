"""
This module handles Covid Updates cases
"""

import json
import time
import json
from time_configure import time_configure
import logging
from uk_covid19 import Cov19API


def parse_csv_data(filename_csv: str = 'nation_2021 -10-28.csv') -> list:
    """Function takes a csv file and returns a list of strings for the rows in the file."""
    with open(filename_csv, "r") as file:
        list_of_lines = file.readlines()
        return list_of_lines


def process_covid_csv_data(covid_csv_data: list) -> tuple:
    """Function takes a list of data from an argument called covid csv data,
    and returns three variables; the number of cases in the last 7 days,
    the current number of hospital cases and the cumulative number of deaths,
    as contained in the given csv file."""

    last_7_days_cases = 0  # initiate variables
    total_hospitalised = 0
    total_deaths = 0
    deaths_updated = False  # flags to find the newest data
    current_hospitalised_updated = False
    for i in range(1, len(covid_csv_data)):  # skip names of columns
        day = covid_csv_data[i]
        day = day.split(",")

        if 2 < i < 10:  # ignore first and second day that are incomplete
            day_cases = int(day[-1])

            last_7_days_cases += day_cases

        try:
            day_hospitalised = int(day[5])
        except ValueError:  # No data for this day
            day_hospitalised = False

        if day_hospitalised and (not current_hospitalised_updated):
            current_hospitalised_updated = True  # unflag flag
            total_hospitalised = day_hospitalised

        try:
            cum_death = int(day[4])
        except ValueError:  # Date has not yet been updated
            cum_death = False

        if cum_death and (not deaths_updated):
            deaths_updated = True  # unflag flag
            total_deaths = cum_death

        if i >= 10 and deaths_updated and current_hospitalised_updated:
            # check whether all information has been found
            break

    return last_7_days_cases, total_hospitalised, total_deaths


def covid_API_request(location: str = "Exeter", location_type: str = "ltla") -> dict:
    """ Function accesses current COVID-19 data using
    the uk-covid-19 module provided by Public Health England.
    Then it returns up-to-date Covid data as a dictionary."""
    filters = [
        f'areaType={location_type}',
        f'areaName={location}'
    ]  # set filters
    if location_type == "nation":
        cases_and_deaths = {
            "areaName": "areaName",
            "date": "date",
            "newCasesByPublishDate": "newCasesByPublishDate",
            "cumCasesBySpecimenDate": "cumCasesBySpecimenDate",
            "hospitalCases": "hospitalCases"
        }
    else:
        cases_and_deaths = {
            "areaCode": "areaCode",
            "areaName": "areaName",
            "areaType": "areaType",
            "date": "date",
            "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
            "hospitalCases": "hospitalCases",
            "newCasesBySpecimenDate": "newCasesBySpecimenDate"

        }  # set structure of the data

    api = Cov19API(filters=filters, structure=cases_and_deaths)

    api_data = api.get_json()  # access data

    return api_data


def nation_cases_parse(nation_data: dict) -> tuple:
    """Function receives a JSON of nation_covid_data and process it. It returns tuple of
    total_cases_over_week, total_hospital_cases_over_week, total_deaths.
    Function consider missing values, but assumes that data for cumulative cases
    was present last week. """

    import logging
    logging.basicConfig(filename='sys.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    # parse covid_api_nation_request
    days = nation_data['data']
    total_cases_over_week = 0
    total_hospital_cases_over_week = 0
    total_deaths = 0
    cumCasesfound = False  # flag to find the newest value
    LIMIT_DAYS = 8

    for i in range(1, len(days)):  # Skip first day due to incomplete data
        day = days[i]
        try:
            total_cases_over_week += int(day["newCasesByPublishDate"])
        except TypeError as e:
            LIMIT_DAYS += 1  # consider later data
            continue
        try:
            total_hospital_cases_over_week += int(day["hospitalCases"])
        except TypeError as e:
            LIMIT_DAYS += 1  # consider later data
            continue
        try:
            cum_death = int(day["cumCasesBySpecimenDate"])
        except TypeError:  # Date has not yet been updated
            cum_death = False

        if cum_death and (not cumCasesfound):
            cumCasesfound = True  # unflag flag
            total_deaths = cum_death
        if i == LIMIT_DAYS:
            if not total_deaths:
                logging.critical("No information about total deaths has been found.")
                total_deaths = 0
            break  # break as we are not interested in later data

    return total_cases_over_week, total_hospital_cases_over_week, total_deaths


def make_data_update(update_name: str, repeated: str = "") -> None:
    """Function updates global variable with updates. It deletes completed events
    from SCHEDULED_EVENTS and replace scheduled updates with completed ones.
     Function doesnt delete repeated updates due to its nature.
    """

    logging.basicConfig(filename='sys.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    logging.info("Making an update")

    import global_variables
    # call combine_covid_api to get an update data
    update_content = combine_covid_API()

    json_content = dict()

    json_content['local_7day_infections'] = update_content[0]

    json_content['national_7day_infections'] = update_content[1]

    json_content['hospital_cases'] = update_content[2]

    json_content['deaths_total'] = update_content[3]

    for i in range(len(global_variables.UPDATES)):
        if repeated:
            continue
        update = global_variables.UPDATES[i]
        if update['title'] == update_name + "_scheduled":  # update UPDATES array
            global_variables.UPDATES[i] = {'title': update_name, 'content': json_content}

            for event in global_variables.SCHEDULED_EVENTS:  # delete scheduled event
                if event.kwargs['update_name'] == update_name:
                    global_variables.SCHEDULED_EVENTS.remove(event)
            return

    global_variables.UPDATES.append({'title': update_name, 'content': json_content})

    return


def combine_covid_API() -> list:

    with open("config.json", "r") as f:
        config = json.load(f)

    location = config['location']
    location_type = config['location_type']
    nation = config['nation']

    # get combined data from two API calls
    json_exeter_data = covid_API_request(location, location_type)
    json_england_data = json.loads(json.dumps(covid_API_request(nation, "nation")))
    # change data so it can apply to covid_csv_data

    exeter_csv_data = [json_exeter_data['data'][0].keys()]
    for day in json_exeter_data['data']:

        line_of_values = ""
        day_values = day.values()

        for value in day_values:
            if (value is None):
                value = ""
            line_of_values += str(value) + ","
        exeter_csv_data.append(line_of_values[:-1])  # get rid of the last ','
    # use process covid_csv_data for a first one

    processed_exeter_data = process_covid_csv_data(exeter_csv_data)

    # use nation_cases_parse to parse nation data
    week_rate_nation = nation_cases_parse(json_england_data)

    # combine the data into one array and return it

    final_data = [processed_exeter_data[0]]
    final_data.extend(week_rate_nation)

    return final_data


def cancel_scheduled_update(update_name: str) -> None:
    """Function cancel scheduled updates by deleting them from SCHEDULED_EVENTS."""
    import logging
    logging.basicConfig(filename='sys.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    import global_variables

    update_name = update_name.replace("_scheduled", "")

    has_been_cancelled = False  # flag to check if update was  cancelled

    for event in global_variables.SCHEDULED_EVENTS:
        if event.kwargs['update_name'] == update_name:
            global_variables.SCHEDULER.cancel(event)
            global_variables.SCHEDULED_EVENTS.remove(event)
            has_been_cancelled = True
            logging.info("Scheduled event has been canceled")

    if not has_been_cancelled:
        logging.critical(f"Scheduled update {update_name} has not been found")


def config_schedule_updates(update_time: str, update_name: str, repeated: str = False) -> None:
    """Function uses update_time in format 'Hours:Minutes' to call time_configure.
    It adds _scheduled to the name of the update.Then it calls schedule_covid_updates."""
    import global_variables
    # change time to a time_difference

    # check if same name updates exist
    same_name_count = 0
    for update in global_variables.UPDATES:

        if update['title'] == update_name + "_scheduled" or update['title'] == update_name:
            same_name_count += 1
    if same_name_count:
        update_name += " (" + str(same_name_count) + ")"

    scheduled_update_name = update_name + "_scheduled"

    scheduled_update_content, update_interval = time_configure(update_time)

    global_variables.UPDATES.append({"title": scheduled_update_name, "content": scheduled_update_content})


    schedule_covid_updates(update_interval, update_name, repeated)


def schedule_covid_updates(update_interval: int, update_name: str, repeated: str = False) -> None:
    """Function uses the sched module to schedule updates to the covid data at the given time interval.
    It appends events to global variable SCHEDULED_EVENTS. For repeated functions
    it schedule a recursive in 24h interval with the same parameters."""
    import global_variables

    event = global_variables.SCHEDULER.enter(update_interval, 0, make_data_update,
                                             kwargs={'update_name': update_name, 'repeated': repeated})

    if (repeated):
        event_2 = global_variables.SCHEDULER.enter(update_interval + 86400, 0, schedule_covid_updates,
                                                   kwargs={'update_interval': update_interval,
                                                           'update_name': update_name, 'repeated': repeated})
        global_variables.SCHEDULED_EVENTS.append(event_2)

    global_variables.SCHEDULED_EVENTS.append(event)

    global_variables.SCHEDULER.run(blocking=False)


if __name__ == "__main__":
    print("covid_data_handler has been called")