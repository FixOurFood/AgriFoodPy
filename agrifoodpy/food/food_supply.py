import numpy as np
import pandas as pd
import os

from ..utils.list_tools import tolist


data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['FAOSTAT']

attribute_names = ['Food', 'Energy', 'Fat', 'Protein']

class FoodSupply:

    def __init__(self, items, years, food = None, energy = None, fat = None, protein = None):

        if np.all(np.array([food, energy, fat, protein]) == None):
            raise ValueError('At least one attribute must be provided for an item, year combination')

        if food is not None : self.food = food
        if energy is not None : self.energy = energy
        if fat is not None : self.fat = fat
        if protein is not None : self.protein = protein

        self.years = years
        self.items = items

        d = {'Item':items, 'Year':years}

        attributes = [food, energy, fat, protein]

        for i in range(len(attributes)):
            if attributes[i] is not None:
                d[attribute_names[i]] = attributes[i]

        self.data = pd.DataFrame(data = d)

    def extract_item(self, items):

        items = tolist(items)
        out_data = self.data[self.data['Item'].isin(items)]

        out_items = out_data['Item'].values
        out_years = out_data['Year'].values

        out_atr = np.repeat(None, len(attribute_names))

        for i ,atr in enumerate(attribute_names):
            try:
                out_atr[i] = out_data[atr].values
            except KeyError:
                pass

        out_food_supply = FoodSupply(out_items, out_years, out_atr[0], out_atr[1], out_atr[2], out_atr[3])

        return out_food_supply

    def extract_year(self, years):

        years = tolist(years)
        out_data = self.data[self.data['Year'].isin(years)]

        out_items = out_data['Item'].values
        out_years = out_data['Year'].values

        out_atr = np.repeat(None, len(attribute_names))

        for i ,atr in enumerate(attribute_names):
            try:
                out_atr[i] = out_data[atr].values
            except KeyError:
                pass

        out_food_supply = FoodSupply(out_items, out_years, out_atr[0], out_atr[1], out_atr[2], out_atr[3])

        return out_food_supply

def __getattr__(name):
    if name not in available:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}.")

    _data_file = f'{data_dir}{name}.csv'
    data = pd.read_csv(_data_file)

    basedata = data[data['Element Code'].isin([10004])]

    food = data[data['Element Code'].isin([10004])]['Value'].values
    energy = data[data['Element Code'].isin([664])]['Value'].values
    protein = data[data['Element Code'].isin([674])]['Value'].values
    fat = data[data['Element Code'].isin([684])]['Value'].values

    years = basedata['Year'].values
    items = basedata['Item Code'].values

    out_supply = FoodSupply(items, years, food, energy, fat, protein)
    return out_supply
