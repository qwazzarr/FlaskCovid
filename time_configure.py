import time


def time_configure(update_time: str) -> tuple:
    """
    function uses time in a format 'HH:MM' to translate it to seconds left. Also function
    considers a missing value for time and assume it as an instant update.
    :param update_time: 'HH:MM' time of the update
    :return: content for an update , seconds until the update
    """
    loc_time = time.asctime()
    loc_time = loc_time.split()
    simple_time = loc_time[3].split(":")  # only HH:MM:SS

    scheduled_update_content = f"Update is planned at {update_time}"

    if update_time == '':  # blank value case
        guessed_time = simple_time
        scheduled_update_content = f"Update is planned at {simple_time[0] + ':' + simple_time[1]}"
    else:
        guessed_time = update_time.split(":")

    hours, minutes, seconds = int(simple_time[0]), int(simple_time[1]), int(simple_time[2])
    ghours, gminutes = int(guessed_time[0]), int(guessed_time[1])

    if (ghours > hours):

        if (gminutes < minutes):
            gminutes += 60
            ghours -= 1
    elif (ghours == hours):

        if (gminutes < minutes):
            ghours += 23
            gminutes += 60

        elif (minutes == gminutes):
            seconds = 0
    elif (ghours < hours):

        ghours += 24

        if (gminutes < minutes):
            ghours -= 1
            gminutes += 60

    update_interval = (3600 * (ghours - hours) + 60 * (gminutes - minutes) - seconds)

    return scheduled_update_content, update_interval
