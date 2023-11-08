""" Module for food intervention models and interfaces with external packages
"""

import xarray as xr
import numpy as np
# from .food_supply import FoodBalanceSheet
import warnings

def balanced_scaling(fbs, items, scale, element, year=None, adoption=None, 
                     timescale=10, origin=None, constant=False,
                     fallback=None):
    """Scale items quantities across multiple elements in a FoodBalanceSheet
    Dataset 
    
    Scales selected item quantities on a food balance sheet and with the
    posibility to keep the sum of selected elements constant.
    Optionally, produce an Dataset with a sequence of quantities over the years
    following a smooth scaling according to the selected functional form.

    The elements used to supply the modified quantities can be selected to keep
    a balanced food balance sheet.

    Parameters
    ----------
    fbs : xarray.Dataset
        Input food balance sheet Dataset.
    items : list
        List of items to scale in the food balance sheet.
    element : string
        Name of the DataArray to scale.
    scale : float
        Scaling parameter after full adoption.
    year : int, optional
        Year of the Food Balance Sheet to use. If not set, the last year of the 
        array is used
    adoption : string, optional
        Shape of the scaling adoption curve. "logistic" uses a logistic model
        for a slow-fast-slow adoption. "linear" uses a constant slope adoption
        during the the "timescale period"
    timescale : int, optional
        Timescale for the scaling to be applied completely.  If "year" +
        "timescale" is greater than the last year in the array, it is extended
        to accomodate the extra years.
    origin : string, optional
        Name of the DataArray which will be used to balance the food balance
        sheets. Any change to the "element" DataArray will be reflected in this
        DataArray.
    constant : bool, optional
        If set to True, the sum of element remains constant by scaling the non
        selected items accordingly.
    fallback : string, optional
        Name of the DataArray used to provide the excess required to balance the
        food balance sheet in case the "origin" falls below zero.

    Returns
    -------
    data : xarray.Dataarray
        Food balance sheet Dataset with scaled "food" values.
    """

    # Check for single item inputs
    if np.isscalar(items):
        items = [items]

    # Check for single item list fbs
    input_item_list = fbs.Item.values
    if np.isscalar(input_item_list):
        input_item_list = [input_item_list]
        if constant:
            warnings.warn("Constant set to true but input only has a single item.")
            constant = False

    # If no items are provided, we scale all of them.
    if items is None or np.sort(items) is np.sort(input_item_list):
        items = fbs.Item.values
        if constant:
            warnings.warn("Cannot keep food constant when scaling all items.")
            constant = False

    # Define Dataarray to use as pivot
    if "Year" in fbs.dims:
        if year is None:
            if np.isscalar(fbs.Year.values):
                year = fbs.Year.values
                fbs_toscale = fbs
            else:
                year = fbs.Year.values[-1]
                fbs_toscale = fbs.isel(Year=-1)
        else:
            fbs_toscale = fbs.sel(Year=year)

    else:
        fbs_toscale = fbs
        try:
            year = fbs.Year.values
        except AttributeError:
            year=0

    # Define scale array based on year range
    if adoption is not None:
        if adoption == "linear":
            from agrifoodpy.utils.scaling import linear_scale as scale_func
        elif adoption == "logistic":
            from agrifoodpy.utils.scaling import logistic_scale as scale_func
        else:
            raise ValueError("Adoption must be one of 'linear' or 'logistic'")
        
        scale_arr = scale_func(year, year, year+timescale-1, year+timescale-1,
                               c_init=1, c_end = scale)
        
        fbs_toscale = fbs_toscale * xr.ones_like(scale_arr)
    
    else:
        scale_arr = scale

    # Create a deep copy to modify and return
    out = fbs_toscale.copy(deep=True)
    osplit = origin.split("-")[-1]
    
    out = out.fbs.scale_add(element, osplit, scale_arr, items, 
                            add = origin.startswith("-"))
    

    if constant:

        delta = out[element] - fbs_toscale[element]

        # Scale non selected items
        non_sel_items = np.setdiff1d(fbs_toscale.Item.values, items)
        non_sel_scale = (fbs_toscale.sel(Item=non_sel_items)[element].sum(dim="Item") - delta.sum(dim="Item")) / fbs_toscale.sel(Item=non_sel_items)[element].sum(dim="Item")
        
        # Make sure inf and nan values are not scaled
        non_sel_scale = non_sel_scale.where(np.isfinite(non_sel_scale)).fillna(1.0)

        if np.any(non_sel_scale < 0):
            warnings.warn("Additional consumption cannot be compensated by \
                        reduction of non-selected items")
        
        out = out.fbs.scale_add(element, osplit, non_sel_scale,
                        non_sel_items, add = origin.startswith("-"))

        # If fallback is defined, adjust to prevent negative values
        if fallback is not None:
            df = out[osplit].where(out[osplit] < 0).fillna(0)
            out[fallback.split("-")[-1]] -= np.where(fallback.startswith("-"), 1, -1)*df
            out[osplit] = out[osplit].where(out[osplit] > 0, 0)

    return out