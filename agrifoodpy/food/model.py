""" Module for food intervention models

"""

import xarray as xr
import numpy as np
# from .food_supply import FoodBalanceSheet
import warnings

def balanced_scaling(fbs, element, items, scale, origin="imports", constant=True,
                      fallback="exports", adoption="logistic", timescale=10,
                      start_year=None):
    """ Scale the consumption of selected items.
    
    Scales consumption on a food balance sheet. The speed at which the adoption
    takes place is defined by the timescale parameter which sets the shape of
    the logistic function.

    To accomodate for the required additional or reduced consumption, "imports",
    "exports" or production can be adjusted to keep the food balance sheet
    balanced. If the quantities on these DataArrays are not enough to provide
    the required consumption, then the remaining is taken out of the "fallback"
    DataArray.

    The scaling is applied to the selected "items" list. If "constant" is set to
    True, then the items not selected in the list are scaled multiplicatively to
    ensure that the sum of the "food" DataArray remains constant.

    Parameters
    ----------
    fbs : xarray.Dataset
        Input food balance sheet Dataset
    items : list
        List of items to scale in the food balance sheet
    scale : float
        Consumed food scaling parameter after full adoption 
    timescale : int
        Number of year the scaling takes to be applied completely
    origin : string, optional
        Name of the DataArray which will be used to balance the food balance
        sheets. Any change to the "food" DataArray will be reflected in this
        DataArray.
    constant : bool, optional
        If set to True, the sum of "food" remains constant by scaling the non
        selected items accordingly.
    fallback : string, optional
        Name of the DataArray used to provide the excess required to balance the
        food balance sheet in case the "origin" falls below zero.
    adoption : string
        Shape of the scaling adoption curve. "logistic" uses a logistic model
        for a slow-fast-slow adoption. "linear" uses a constant slope adoption
        during the the "timescale period"
    start_year : int
        Year at which the scaling start. "start_year" + "timescale" must be
        greater or equal than the last year of the "Year" coordinate.

    Returns
    -------
    data : xarray.Dataarray
        Food balance sheet Dataset with scaled "food" values.
    """

    # Check for single item inputs
    if np.isscalar(items):
        items = [items]

    # Check for single item list fbs
    input_item_list = fbs.Item.values.tolist()
    if np.isscalar(input_item_list):
        input_item_list = [input_item_list]
        if constant:
            warnings.warn("Constant set to true but input only has one item.")
            constant = False
    else:
        sel = {"Item":items}

    # If no items are provided, we scale all of them.
    if items is None or np.sort(items) is np.sort(input_item_list):
        items = fbs.Item.values
        if constant:
            warnings.warn("Cannot keep food constant when scaling all items.")
            constant = False

    # Create a deep copy to modify and return
    out = fbs.copy(deep=True)

    # Scale items
    years = fbs.Year.values
    if start_year is None:
        start_year = years[0]

    if adoption == "linear":
        from agrifoodpy.utils.scaling import linear_scale as scale_func
    else:
        from agrifoodpy.utils.scaling import logistic_scale as scale_func

    scale_arr = scale_func(years[0], start_year, start_year+timescale,
                                 years[-1], c_init=1, c_end = scale)
    
    out = out.fbs.scale_add(element, origin.split("-")[-1], scale_arr, items,
                    add = origin.startswith("-"))
    
    delta = out[element] - fbs[element]

    if constant:
        # non selected items
        non_sel_items = np.setdiff1d(fbs.Item.values, items)
        non_sel_scale = (fbs.sel(Item=non_sel_items)["food"].sum(dim="Item") - delta.sum(dim="Item")) / fbs.sel(Item=non_sel_items)["food"]

        if np.any(non_sel_scale < 0):
            warnings.warn("Additional consumption cannot be compensated by \
                          reduction of non-selected items")
        
        # add = not origin.startswith("-")
        out = out.fbs.scale_add(element, origin.split("-")[-1], non_sel_scale,
                        non_sel_items, add = origin.startswith("-"))
        
    delta_fallback = out[origin.split("-")[-1]].where(out[origin.split("-")[-1]] < 0).fillna(0)

    out[fallback.split("-")[-1]] -= np.where(fallback.startswith("-"), 1, -1) * delta_fallback

    out[origin.split("-")[-1]] = out[origin.split("-")[-1]].where(out[origin.split("-")[-1]] > 0, 0)

    return out