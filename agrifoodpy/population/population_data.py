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
    quantities : ([nd], ny, nr) ndarray
        Array containing the population for each combination of `Year` and
        `Region`.
    datasets : (nd,) array_like, optional
        Array with model name strings. If provided, a dataset is created
        for each element in `datasets` with the quantities being each of the
        sub-arrays indexed by the last coordinate of the input array.
    long_format : bool
        Boolean flag to interpret data in long or wide format

    Returns
    -------
    data : xarray.Dataset
        Population dataset containing the population for each `Year` and
        `Region` with one dataarray per element in `dataset`.
    """

    # if the input has a single element, proceed with long format
    if np.isscalar(quantities):
        long_format = True

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
        # dataset, quantities
        ndims = 2
    else:
        # dataset, year, region
        ndims = 3

    # make sure the long format has the right number of dimensions
    while len(quantities.shape) < ndims:
        quantities = np.expand_dims(quantities, axis=0)

    # If no dataset names are given, then create generic ones, one for each
    # dataset
    if datasets is None:
        datasets = [f"Population {id}" for id in range(quantities.shape[0])]

    # Else, if a single string is given, transform to list. If doesn't match
    # the number of datasets created above, xarray will return an error.
    elif isinstance(datasets, str):
        datasets = [datasets]

    if long_format:
        # Create a datasets, one at a time
        for id, dataset in enumerate(datasets):
            values = np.zeros(size)*np.nan
            values[tuple(ii)] = quantities[id]
            data[dataset] = (coords, values)

    else:
        quantities = quantities[:, ii[0]]
        if len(quantities.shape) < ndims:
            quantities = np.expand_dims(quantities, axis=0)

        quantities = quantities[..., ii[1]]
        if len(quantities.shape) < ndims:
            quantities = np.expand_dims(quantities, axis=0)
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
