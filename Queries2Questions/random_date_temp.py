from datetime import datetime, date
import random

def add_suffix(num):
    """
    Given a number, add the appropriate suffix (st, nd, rd, or th) to it and return as a string.
    """
    if 11 <= num <= 13:
        suffix = "th"
    else:
        last_digit = num % 10
        if last_digit == 1:
            suffix = "st"
        elif last_digit == 2:
            suffix = "nd"
        elif last_digit == 3:
            suffix = "rd"
        else:
            suffix = "th"
    return f"{num}{suffix}"


date_string = "1843-06-05"
# date_templates = ["%Y/%m/%d", "%Y-%m-%d", "%B "+add_suffix(date.day) +", %Y"]

# List of date templates
date_templates = [
    "%Y/%m/%d", 
    "%Y-%m-%d",
    "{month} {day_suffix}, {year}",
    "the {day_suffix} of {month} in {year}"
]

def date_string(date_str):

    template = random.choice(date_templates)
    date_object=datetime.strptime(date_str, "%Y-%m-%d")

    if "{day_suffix}" in template:
        date_text = template.format(day_suffix=add_suffix(date_object.day), month=date_object.strftime("%B"), year=date_object.year)
    else:
        date_text = date_object.strftime(template)

    return date_text
# date_object=datetime.strptime(date_string, "%Y-%m-%d")

# print(date_text)
