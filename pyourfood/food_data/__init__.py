import os
import pandas as pd
import numpy as np


class FAOSTAT:

    FAOSTAT_file = os.path.join(os.path.dirname(__file__), 'data/food_supply_data.csv')
    data = pd.read_csv(FAOSTAT_file)
    years = np.unique(data['Year'])
    item_names = np.unique(data['Item'])
    item_codes = np.unique(data['Item Code'])
    elements = np.unique(data['Element'])
    elements_codes = np.unique(data['Element Code'])
