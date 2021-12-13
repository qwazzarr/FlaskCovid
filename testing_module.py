



from covid_data_handler import *
from covid_news_handling import *
import global_variables


def test_parse_csv_data():
    data = parse_csv_data('nation_2021 -10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data ('nation_2021 -10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')


def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news('test')

def test_config_news_update() :
    config_news_update(update_time= "23:10", update_name = "Test", repeated = False, with_covid = False)
    is_in_update = False
    is_in_events = False
    for update in global_variables.UPDATES:
        if update['title'] == "Test_scheduled":
            is_in_update = True
            break
    for event in global_variables.SCHEDULED_EVENTS:
        if event.kwargs['update_name'] == "Test":
            is_in_events = True
            break
    assert is_in_events
    assert is_in_update

#time config




