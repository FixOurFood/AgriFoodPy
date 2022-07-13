import numpy as np
import xarray as xr
import os

from ..utils.list_tools import tolist

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['FAOSTAT']

def FoodSupply(items, years, quantities, regions=None, elements=None):

    _years = np.unique(years)
    _items = np.unique(items)

    size = (len(_years), len(_items))

    ii = [np.searchsorted(_years, years), np.searchsorted(_items, items)]

    coords = {"Year" : _years,
              "Item" : _items}

    if regions is not None:
        _regions = np.unique(regions)
        ii.append(np.searchsorted(_regions, regions))
        size = size + (len(_regions),)
        coords["Region"] = _regions

    if elements is not None:
        _elements = np.unique(elements)
        ii.append(np.searchsorted(_elements, elements))
        coords["Element"] = _elements
        size = size + (len(_elements),)

    values = np.zeros(size)*np.nan

    values[tuple(ii)] = quantities

    data = xr.Dataset(data_vars = dict(value=(coords.keys(), values)), coords = coords)

    return data

def __getattr__(name):
    if name not in available:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}.")

    _data_file = f'{data_dir}{name}.nc'
    data = xr.open_dataset(_data_file)

    return data
