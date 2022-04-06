import numpy as np
import pandas as pd
from .utils.list_tools import tolist

def extract_item(in_data, item):
    item = tolist(item)
    out_data = in_data[in_data['Item Code'].isin(item)]
    return out_data

def extract_year(in_data, year):
    year = tolist(year)
    out_data = in_data[in_data['Year'].isin(year)]
    return out_data

def food_supply(in_data, item=None, year=None):

    if item is None:
        item = np.unique(in_data['Item Code'])

    if year is None:
        year = np.unique(in_data['Year'])

    out_data = in_data[in_data['Element Code'] == 10004]
    out_data = extract_year(out_data, year)
    out_data = extract_item(out_data, item)

    return out_data['Value']

def energy_supply(in_data, item=None, year=None):

    if item is None:
        item = np.unique(in_data['Item Code'])

    if year is None:
        year = np.unique(in_data['Year'])

    out_data = in_data[in_data['Element Code'] == 664]
    out_data = extract_year(out_data, year)
    out_data = extract_item(out_data, item)

    return out_data['Value']

def protein_supply_quantity(in_data, item=None, year = None):

    if item is None:
        item = np.unique(in_data['Item Code'])

    if year is None:
        year = np.unique(in_data['Year'])

    out_data = extract_item(in_data, item)
    out_data = extract_year(out_data, year)
    out_data = out_data[out_data['Element Code'] == 674]

    return out_data['Value']

def fat_supply_quantity(in_data, item=None, year = None):

    if item is None:
        item = np.unique(in_data['Item Code'])

    if year is None:
        year = np.unique(in_data['Year'])

    out_data = extract_item(in_data, item = item)
    out_data = extract_year(out_data, year = year)
    out_data = out_data[out_data['Element Code'] == 684]

    return out_data['Value']
