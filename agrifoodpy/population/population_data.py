import numpy as np
import pandas as pd
import os

from ..utils.list_tools import tolist

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['UN_world_1950_2019', 'UN_world_2020_2100']

class Population:

    def __init__(self, regions, years, populations):

        self.regions = regions
        self.years = years
        self.populations = populations
        self.data = pd.DataFrame({'Region':tolist(regions), 'Year':tolist(years),
                                    'Population':tolist(populations)})

    def extract_region(self, regions):

        regions = tolist(regions)
        out_data = self.data[self.data['Region'].isin(regions)]

        out_regions = out_data['Region'].values
        out_years = out_data['Year'].values
        out_pops = out_data['Population'].values

        out_population = Population(out_regions, out_years, out_pops)

        return out_population

    def extract_year(self, years):

        years = tolist(years)
        out_data = self.data[self.data['Year'].isin(years)]

        out_regions = out_data['Region'].values
        out_years = out_data['Year'].values
        out_pops = out_data['Population'].values

        out_population = Population(out_regions, out_years, out_pops)

        return out_population

def __getattr__(name):
    if name not in available:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}.")

    _data_file = f'{data_dir}{name}.csv'
    data = pd.read_csv(_data_file)

    regions = data['LocID'].values
    years = data['Time'].values
    pops = data['PopTotal'].values

    out_pop = Population(regions, years, pops)
    return out_pop
