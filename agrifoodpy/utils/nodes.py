import copy
import json
import os
import xarray as xr
import numpy as np
import importlib

from ..pipeline import standalone
from ..utils.dict_utils import get_dict, set_dict


@standalone(["dataset"], ["dataset"])
def add_items(
    dataset,
    items,
    values=None,
    copy_from=None,
    datablock=None
):
    """Adds a list of items to a selected dataset in the datablock and
    initializes their values.

    Parameters
    ----------
    datablock : Datablock
        Datablock object.
    dataset : dict
        Datablock path to the datasets to modify.
    items : list, dict
        List of items or dictionary of items attributes to add. If a
        dictionary, keys are the item names, and non-dimension coordinates.
    values : list, optional
        List of values to initialize the items. If not set, values are set to
        0, unless the copy from parameter is set.
    copy_from : list, optional
        Items to copy the values from.

    Returns
    -------
    dict or xarray.Dataset
        - If no datablock is provided, returns a xarray.Dataset with the new
          items.
        - If a datablock is provided, returns the datablock with the modified
          datasets on the corresponding keys.

    """

    # Check if items is a dictionary
    if isinstance(items, dict):
        items_src = copy.deepcopy(items)
        new_items = items_src.pop("Item")
    else:
        new_items = items
        items_src = {}

    # Add new items to the datasets
    data = get_dict(datablock, dataset)

    data = data.fbs.add_items(new_items, copy_from=copy_from)
    for key, val in items_src.items():
        data[key].loc[{"Item": new_items}] = val

    if values is not None:
        data.loc[{"Item": new_items}] = values

    elif copy_from is None:
        data.loc[{"Item": new_items}] = 0

    set_dict(datablock, dataset, data)

    return datablock


@standalone(["dataset"], ["dataset"])
def add_years(
    dataset,
    years,
    projection='empty',
    datablock=None
):
    """
    Extends the Year coordinates of a dataset.

    Parameters
    ----------
    datablock : dict
        The datablock dictionary where the dataset is stored.
    dataset : str
        Datablock key of the dataset to extend.
    years : list
        List of years to extend the dataset to.
    projection : str
        Projection mode. If "constant", the last year of the input array
        is copied to every new year. If "empty", values are initialized and
        set to zero. If a float array is given, these are used to populate
        the new year using a scaling of the last year of the array
    """

    data = get_dict(datablock, dataset)

    data = data.fbs.add_years(years, projection)

    set_dict(datablock, dataset, data)

    return datablock


def copy_datablock(datablock, key, out_key):
    """Copy a datablock element into a new key in the datablock

    Parameters
    ----------
    datablock : xarray.Dataset
        The datablock to print
    key : str
        The key of the datablock to print
    out_key : str
        The key of the datablock to copy to

    Returns
    -------
    datablock : dict
        Datablock to with added key
    """

    datablock[out_key] = copy.deepcopy(datablock[key])

    return datablock


def print_datablock(
    datablock,
    key,
    attr=None,
    method=None,
    args=None,
    kwargs=None,
    preffix="",
    suffix=""
):
    """Prints a datablock element or its attributes/methods at any point in the
    pipeline execution.

    Parameters
    ----------
    datablock : dict
        The datablock to print from.
    key : str
        The key of the datablock to print.
    attr : str, optional
        Name of an attribute of the object to print.
    method : str, optional
        Name of a method of the object to call and print.
    args : list, optional
        Positional arguments for the method call.
    kwargs : dict, optional
        Keyword arguments for the method call.

    Returns
    -------
    datablock : dict
        Unmodified datablock to continue execution.
    """
    obj = datablock[key]

    # Extract attribute
    if attr is not None:
        if hasattr(obj, attr):
            obj = getattr(obj, attr)
        else:
            print(f"Object has no attribute '{attr}'")
            return datablock

    # Call method
    if method is not None:
        if hasattr(obj, method):
            func = getattr(obj, method)
            if callable(func):
                args = args or []
                kwargs = kwargs or {}
                try:
                    obj = func(*args, **kwargs)
                except Exception as e:
                    print(f"Error calling {method} on {key}: {e}")
                    return datablock
            else:
                print(f"'{method}' is not callable on {key}")
                return datablock
        else:
            print(f"Object has no method '{method}'")
            return datablock

    # Final print
    print(f"{preffix}{obj}{suffix}")
    return datablock


def write_to_datablock(datablock, key, value, overwrite=True):
    """Writes a value to a specified key in the datablock.

    Parameters
    ----------
    datablock : dict
        The datablock to write to.
    key : str
        The key in the datablock where the value will be written.
    value : any
        The value to write to the datablock.
    overwrite : bool, optional
        If True, overwrite the existing value at the key.
        If False, do not overwrite.

    Returns
    -------
    datablock : dict
        The updated datablock with the new key-value pair.
    """

    if not overwrite and key in datablock:
        raise KeyError(
            "Key already exists in datablock and overwrite is set to False.")

    set_dict(datablock, key, value)

    return datablock


def _import_dataset(module_name, dataset_name):
    module = importlib.import_module(module_name)
    dataset = getattr(module, dataset_name)
    return dataset


@standalone([], ['datablock_path'])
def load_dataset(
    datablock_path,
    path=None,
    module=None,
    data_attr=None,
    da=None,
    coords=None,
    scale=1.,
    datablock=None
):
    """Loads a dataset to the specified datablock dictionary.

    Parameters
    ----------
    datablock : dict
        The datablock path where the dataset is stored
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
        Optional multiplicative factor to be applied to the dataset on load.
    datablock_path : str
        The path to the datablock where the dataset is stored.

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
        dataset = _import_dataset(module, data_attr)

    # Select dataarray and coords from dataset
    if da is not None:
        dataset = dataset[da]

    if coords is not None:
        dataset = dataset.sel(coords)

    # Add dataset to datablock
    datablock[datablock_path] = dataset * scale

    return datablock

def _tuple_to_str(tup):
    return ".".join(str(x) for x in tup)

def write_json(datablock, key, path, indent=2):
    """Writes a datablock value to a JSON file.

    Parameters
    ----------
    datablock : dict
        The datablock to read from.
    key : str, tuple or list
        List of datablock keys (or tuple of keys for nested access) of the
        value to write.
    path : str
        Output file path.
    indent : int, optional
        JSON indentation level. Defaults to 2.

    Returns
    -------
    datablock : dict
        Unmodified datablock.
    """

    def _default(o):
        if isinstance(o, (xr.Dataset, xr.DataArray)):
            return o.to_dict()
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        return str(o)

    if isinstance(key, str):
        key = [key]
    elif isinstance(key, tuple):
        key = [key]

    obj_dict = {}

    for obj_key in key:
        if isinstance(obj_key, tuple):
            obj_dict[_tuple_to_str(obj_key)] = get_dict(datablock, obj_key)
        else:
            obj_dict[obj_key] = get_dict(datablock, obj_key)
    
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    with open(path, "w") as f:
        json.dump(obj_dict, f, indent=indent, default=_default)

    return datablock


def write_netcdf(datablock, key, path):
    """Writes a datablock xarray Dataset or DataArray to a NetCDF file.

    Parameters
    ----------
    datablock : dict
        The datablock to read from.
    key : str or tuple
        Datablock key (or tuple of keys for nested access) of the dataset to
        write.
    path : str
        Output file path.

    Returns
    -------
    datablock : dict
        Unmodified datablock.
    """

    obj = get_dict(datablock, key)

    if not isinstance(obj, (xr.Dataset, xr.DataArray)):
        raise TypeError(
            f"write_netcdf only supports xarray Dataset or DataArray objects. "
            f"Got {type(obj).__name__} instead."
        )

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    obj.to_netcdf(path)

    return datablock


def write_csv(datablock, key, path, index=True):
    """Writes a datablock value to a CSV file.

    Supports xarray Dataset, xarray DataArray, pandas DataFrame and Series.
    xarray objects are converted to a DataFrame before writing; the
    multi-index produced by that conversion (which encodes coordinates) is
    written when index=True.

    Parameters
    ----------
    datablock : dict
        The datablock to read from.
    key : str, list or tuple
        Datablock key (or tuple of keys for nested access) of the value to write.
    path : str
        Output file path.
    index : bool, optional
        Whether to write the row index. Defaults to True.

    Returns
    -------
    datablock : dict
        Unmodified datablock.
    """
    import pandas as pd

    obj = get_dict(datablock, key)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    if isinstance(obj, (xr.Dataset, xr.DataArray)):
        try:
            obj.to_dataframe().to_csv(path, index=index)
        except ValueError:
            # Unnamed DataArrays raise a ValueError.
            if isinstance(key, tuple):
                obj.name = key[-1]
            else:
                obj.name = str(key)

            obj.to_dataframe().to_csv(path, index=index)

    elif isinstance(obj, (pd.DataFrame, pd.Series)):
        obj.to_csv(path, index=index)
    else:
        raise TypeError(
            f"write_csv does not support objects of type {type(obj).__name__}. "
            "Expected xr.Dataset, xr.DataArray, pd.DataFrame, or pd.Series."
        )

    return datablock


def write_text(datablock, key, path):
    """Writes the string representation of a datablock value to a text file.

    Parameters
    ----------
    datablock : dict
        The datablock to read from.
    key : str or tuple
        Datablock key (or tuple of keys for nested access) of the value to write.
    path : str
        Output file path.

    Returns
    -------
    datablock : dict
        Unmodified datablock.
    """

    obj = get_dict(datablock, key)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    with open(path, "w") as f:
        f.write(str(obj))

    return datablock
