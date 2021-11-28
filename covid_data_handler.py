

def parse_csv_data(filename_csv):
    '''Function takes an argument called csv filename and returns a list of strings for the rows in the file.'''
    pass

def process_covid_csv_data(covid_csv_data):
    '''Function takes a list of data from an argument called covid csv data,
    and returns three variables; the number of cases in the last 7 days,
    the current number of hospital cases and the cumulative number of deaths, as contained in the given csv file.'''
    pass

def covid_API_request(location = "Exeter", location_type = "ltla"):
    ''' Function accesses current COVID-19 data using
    the uk-covid-19 module provided by Public Health England.
    Then it returns up-to-date Covid data as a dictionary.'''
    pass

def schedule_covid_updates(update_interval, update_name):
    '''Function uses the sched module to schedule updates to the covid data at the given time interval.'''
    pass

