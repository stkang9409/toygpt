from datetime import datetime


def required_report_num(start_date: datetime, today: datetime):
    # start_date ~ today, count days except sunday, do not count fifth week
    days = (today - start_date).days + 1

    # 29 ~ 35 is 28
    if 29 <= days <= 35:
        days = 28
    elif days > 35:
        days = days - 7

    # count days except sunday
    days -= days // 7
    return days