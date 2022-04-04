import numpy as np
import pandas as pd
from .food_data import FAOSTAT

FAOSTAT_years = FAOSTAT.years
FAOSTAT_item_codes = FAOSTAT.item_codes
FAOSTAT_item_names = FAOSTAT.item_names
FAOSTAT_data = FAOSTAT.data

def _tolist(item):
    item = np.array(item).tolist()
    if not isinstance(item, list):
        item = [item]
    return item

def extract_item(in_data, item):
    item = _tolist(item)
    out_data = in_data[in_data['Item Code'].isin(item)]
    return out_data

def extract_year(in_data, year):
    year = _tolist(year)
    out_data = in_data[in_data['Year'].isin(year)]
    return out_data

def food_supply(in_data, item=FAOSTAT_item_codes, year = FAOSTAT_years):
    out_data = in_data[in_data['Element Code'] == 664]
    out_data = extract_year(out_data, year)
    out_data = extract_item(out_data, item)
    return out_data

def protein_supply_quantity(in_data, item=FAOSTAT_item_codes, year = FAOSTAT_years):
    out_data = extract_item(in_data, item)
    out_data = extract_year(out_data, year)
    out_data = out_data[out_data['Element Code'] == 674]
    return out_data

def fat_supply_quantity(in_data, item=FAOSTAT_item_codes, year = FAOSTAT_years):
    out_data = extract_item(in_data, item = item)
    out_data = extract_year(out_data, year = year)
    out_data = out_data[out_data['Element Code'] == 684]
    return out_data
