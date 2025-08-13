import numpy as np
import xarray as xr
import importlib

from agrifoodpy.pipeline import standalone

def import_dataset(module_name, dataset_name):
    module = importlib.import_module(module_name)
    dataset = getattr(module, dataset_name)
    return dataset

@standalone([], ['datablock_path'])
def load_dataset(datablock_path="data", path=None, module=None,
                    data_attr=None, da=None, coords=None, scale=1.,
                    datablock=None):
    """Loads a dataset to the specified datablock dictionary. Can only be used
    in pipeline mode.

    Parameters
    ----------
    datablock : dict
        The datablock dictionary where the dataset is stored, containing all
        the model parameters
    datablock_path : str
        The path to the datablock where the dataset is stored.
    path : str
        The path to the dataset stored in a netCDF file.
    module : str
        The module name where the dataset will be imported from.
    data_attr : str
        The attribute name of the dataset in the module.
    da : str
        The dataarray to be loaded.
    coords : dict
        Dictionary containing the coordinates of the dataset to be loaded.
    scale : float
        Optional scale factor to be applied to the dataset on load.

    """

    # Load dataset from Netcdf file
    if path is not None:
        try:
            with xr.open_dataset(path) as data:
                dataset = data.load()
        
        except ValueError:
            with xr.open_dataarray(path) as data:
                dataset = data.load()

    # Load dataset from module
    elif module is not None and data_attr is not None:
        dataset = import_dataset(module, data_attr)

    # Select dataarray and coords from dataset
    if da is not None:
        dataset = dataset[da]
        
    if coords is not None:
        dataset = dataset.sel(coords)

    # Add dataset to datablock
    datablock[datablock_path] = dataset * scale

    return datablock
