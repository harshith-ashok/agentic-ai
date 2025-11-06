from datetime import date, timedelta


def get_week_info(date_value):
    year = date_value.year
    week_number = date_value.isocalendar()[1]
    first_day_of_year = date(year, 1, 1)
    days_to_first_monday = (first_day_of_year.weekday() - 0) % 7
    first_monday = first_day_of_year + timedelta(days=-days_to_first_monday)
    week_start = first_monday + timedelta(weeks=week_number-1)
    week_end = week_start + timedelta(days=6)

    return year, week_start.month, week_start.day
