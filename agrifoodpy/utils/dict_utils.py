"""Pipeline utilities"""

import numpy as np


def item_parser(fbs, items):
    """Extracts a list of items from a dataset using a coordinate-key tuple,
    or converts a scalar item to a list

    Parameters
    ----------

    fbs : xarray.Dataset or xarray.DataArray
        The dataset containing the coordinate-key to extract items from.
    items : tuple, scalar
        If a tuple, the first element is the name of the coordinate and the
        second element is a list of items to extract. If a scalar, the item
        is converted to a list.

    Returns
    -------
    list
        A list of items matching the coordinate-key description, or containing
        the scalar item.
    """

    if items is None:
        return None

    if isinstance(items, tuple):
        items = fbs.sel(Item=fbs[items[0]].isin(items[1])).Item.values
    elif np.isscalar(items):
        items = [items]

    return items


def get_dict(datablock, keys):
    """Returns an element from a dictionary using a key or tuple of keys used
    to describe a path of keys

    Parameters
    ----------

    datablock : dict
        The input dictionary
    keys : str or tuple
        Dictionary key, or tuple of keys
    """

    if isinstance(keys, tuple):
        out = datablock
        for key in keys:
            out = out[key]
    else:
        out = datablock[keys]

    return out


def set_dict(datablock, keys, object, create_missing=True):
    """Sets an element in a dictionary using a key or tuple of keys used to
    describe a path of keys

    Parameters
    ----------

    datablock : dict
        The input dictionary
    keys : str or tuple
        Dictionary key, or tuple of keys
    object : any
        The object to set in the dictionary
    create_missing : bool, optional
        If True, creates missing keys in the dictionary. Defaults to True.

    Raises
    ------
    KeyError
        If a key in the path does not exist and create_missing is False.
    """

    if isinstance(keys, tuple):
        out = datablock
        for key in keys[:-1]:
            if key not in out:
                if create_missing:
                    out[key] = {}
                else:
                    raise KeyError(f"Key '{key}' not found in datablock.")
            out = out[key]
        out[keys[-1]] = object
    else:
        datablock[keys] = object
