"""Population module.
"""

import numpy as np
import pandas as pd
import os
import xarray as xr

from ..utils.list_tools import tolist

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['UN']

def __getattr__(name):
    if name not in available:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}.")

    _data_file = f'{data_dir}{name}.nc'
    data = xr.open_dataset(_data_file)

    return data
