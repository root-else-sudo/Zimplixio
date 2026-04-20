from datetime import datetime


def format_date(d):
    return d.strftime('%A, %B ') + str(d.day) + d.strftime(', %Y')


def format_time(d, t):
    dt = datetime.combine(d, t)
    return dt.strftime('%I:%M %p').lstrip('0') or '12:00 AM'
