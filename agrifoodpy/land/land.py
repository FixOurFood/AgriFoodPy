"""Land module.
"""

import numpy as np
import xarray as xr
import os
from itertools import product

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )

resolutions = [100, 200, 500, 1000, 2000]
datasets = ["CEH", "ALC", "CEHLCdomagg", "CEHLCdomtar", "CEHLCperagg", "CEHLCpertar"]
arrays = [f"{d}_{r}" for d, r in product(datasets, resolutions)]

def __getattr__(name):
    if name not in arrays:
        raise AttributeError(f"{name!r} does not match a dataset and resoliution in {__name__!r}.")

    dataset, resolution = name.split('_')
    _data_file = f'{data_dir}{dataset}/{name}.nc'
    data = xr.open_dataset(_data_file)

    return data
