from django import template

from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def timedelta(timedelta, string_format=None):
    if timedelta is None:
        return ""

    total_seconds = int(timedelta.total_seconds())

    if string_format == "U":
        return total_seconds

    seconds_in_minute = 60
    seconds_in_hour = seconds_in_minute * 60
    seconds_in_day = seconds_in_hour * 24

    days = timedelta.days
    hours = (total_seconds % seconds_in_day) // seconds_in_hour
    minutes = (total_seconds % seconds_in_hour) // seconds_in_minute
    seconds = (total_seconds % seconds_in_minute)

    if string_format is None:
        string_format = ""
        if days:
            string_format += "{day} day"
            if days != 1:
                string_format += 's'
        if hours:
            if string_format:
                string_format += ", "
            string_format += "{hour} hour"
            if hours != 1:
                string_format += 's'
        if minutes:
            if string_format:
                string_format += ", "
            string_format += "{minute} minute"
            if minutes != 1:
                string_format += "s"

    return string_format.format(day=days, hour=hours, minute=minutes, second=seconds)