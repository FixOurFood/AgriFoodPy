import xarray as xr
import numpy as np
import copy

from ..pipeline import standalone
from ..utils.dict_utils import get_dict, set_dict
from ..food import food

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
        List of items or dictionary of items attributes to add. If a dictionary,
        keys are the item names, and non-dimension coordinates. Must contain a
        key named "Item".
    values : list, optional
        List of values to initialize the items. If not set, values are set to 0,
        unless the copy from parameter is set.
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
        data[key].loc[{"Item":new_items}] = val

    if values is not None:
        data.loc[{"Item":new_items}] = values
        
    elif copy_from is None:
        data.loc[{"Item":new_items}] = 0
    
    set_dict(datablock, dataset, data)

    return datablock
