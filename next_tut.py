from datetime import datetime, timedelta


def get_times(start_date : datetime, end_date, except_dates):
    week = timedelta(weeks=1)

    times = []
    current = start_date
    while current <= end_date:
        if current.date() not in except_dates:
            times.append(current)
        current += week
    return times


def get_next_time(current, dates):
    for date in dates:
        if date > current:
            return date
    return datetime.fromtimestamp(0)



def get_next_tut():
    
    date_format = "%Y%m%d"
    time_format = "%H:%M"

    start_date = datetime.strptime("20230419", date_format)
    end_date = datetime.strptime("20230726", date_format)

    except_dates_str = ["20230531"]
    except_dates = [datetime.strptime(x, date_format).date() for x in except_dates_str]

    start_time = datetime.strptime("11:30", time_format)
    end_time = datetime.strptime("13:00", time_format)
    offset_minutes = 45

    start_date += timedelta(hours=start_time.hour, minutes=start_time.minute) 
    times = get_times(start_date, end_date, except_dates)

    now = datetime.now()    
    next_time = get_next_time(now, times)
    other_time = get_next_time(now - timedelta(minutes=offset_minutes), times)

    if next_time != other_time:
        return [next_time.timestamp(), (other_time + timedelta(minutes=offset_minutes)).timestamp()]    
    
    return [next_time.timestamp(), (next_time + timedelta(minutes=offset_minutes)).timestamp()]
