import numpy as np
import os
import xarray as xr

from ..utils.list_tools import tolist

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['UN']

def population(years, regions, quantities, datasets=None, long_format=True):
    """Population style dataset constructor

    Parameters
    ----------
    years : (ny,) array_like
        The year values for which coordinates will be created.
    regions : (nr,) array_like, optional
        The region identifying ID or strings for which coordinates will be
        created.
    quantities : (ny, nr) ndarray
        Array containing the population for each combination of `Year` and
        `Region`.
    datasets : (nd,) array_like, optional
        Array with model name strings
    long_format : bool
        Boolean flag to interpret data in long or wide format

    Returns
    -------
    data : xarray.Dataset
        Population dataset containing the population for each `Year` and
        `Region` with one dataarray per element in `dataset`.
    """

    quantities = np.array(quantities)

    # Identify unique values in coordinates
    _years = np.unique(years)
    _regions = np.unique(regions)
    coords = {"Year" : _years,
              "Region" : _regions}

    # find positions in output array to organize data
    ii = [np.searchsorted(_years, years), np.searchsorted(_regions, regions)]
    size = (len(_years), len(_regions))

    # Create empty dataset
    data = xr.Dataset(coords = coords)

    if long_format:
        ndims = 2
    else:
        ndims = 3

    # make sure the long format has two dimensions
    # One along years and regions, one along datasets
    while len(quantities.shape) < ndims:
        quantities = np.expand_dims(quantities, axis=0)

    # If no dataset names are given, then create generic ones, one for each
    # dataset
    if datasets is None:
        datasets = [f"Population {id}" for id in range(quantities.shape[0])]

    # Else, if a single string is given, transform to list. If doesn't match
    # the number of datasets created above, this will spit a list later.
    elif isinstance(datasets, str):
        datasets = [datasets]

    if long_format:
        # Create a datasets, one at a time
        for id, dataset in enumerate(datasets):
            values = np.zeros(size)*np.nan
            values[tuple(ii)] = quantities[id]
            data[dataset] = (coords, values)

    else:
        quantities = quantities[:, ii[0], :]
        quantities = quantities[:, :, ii[1]]

        # Create a datasets, one at a time
        for id, dataset in enumerate(datasets):
            values = quantities[id]
            data[dataset] = (coords, values)

    return data

def __getattr__(name):
    if name not in available:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}.")

    _data_file = f'{data_dir}{name}.nc'
    data = xr.open_dataset(_data_file)

    return data
