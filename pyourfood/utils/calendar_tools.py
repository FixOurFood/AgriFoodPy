import numpy as np
import calendar
from .list_tools import tolist

def days_in_year(years):

    years = tolist(years)
    days = np.ones(len(years))*365
    for i, year in enumerate(years):
        if calendar.isleap(year) : days[i] += 1

    return days
