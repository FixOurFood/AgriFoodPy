""" Module for food intervention models and interfaces with external packages
"""

import xarray as xr
import numpy as np
import copy
from ..pipeline import standalone, pipeline_node
from ..utils.dict_utils import get_dict, set_dict, item_parser
import warnings


@standalone(input_keys=["fbs"], return_keys=["out_key"])
def balanced_scaling(
    fbs,
    scale,
    element,
    items=None,
    constant=False,
    padding_items=None,
    origin=None,
    add_to_origin=True,
    elasticity=None,
    fallback=None,
    add_to_fallback=True,
    conversion_arr=None,
    out_key=None,
    datablock=None
):
    """ Scales items in a Food Balance Sheet, while optionally maintaining
    total quantities

    Scales selected item quantities on a Food Balance Sheet, with the option
    to keep the sum over an element DataArray constant.
    Changes can be propagated to a set of origin FBS elements according to an
    elasticity parameter.

    Parameters
    ----------
    fbs : xarray.Dataset
        Input food balance sheet Dataset
    scale : float
        Scaling parameter after full adoption
    element : string
        Name of the DataArray to scale
    items : list, optional
        List of items to scaled in the food balance sheet. If None, all items
        are scaled and 'constant' is ignored
    constant : bool, optional
        If set to True, the sum of element remains constant by scaling the non
        selected items accordingly
    padding_items : list, optional
        List of items to use for scaling when 'constant' is True. If None, all
        non-selected items are used for scaling.
    origin : string, list, optional
        Names of the DataArrays which will be used as source for the quantity
        changes. Any change to the "element" DataArray will be reflected in
        this DataArray
    add_to_origin : bool, array, optional
        Whether to add or subtract the difference from the respective origins
    elasticity : float, array, optional
        Relative fraction of the total difference to be assigned to each origin
        element. Values are not normalized.
    fallback : string
        Name of the DataArray to use as fallback in case the origin quantities
        fall below zero
    add_to_fallback : bool, optional
        Whether to add or subtract the difference below zero in the origin
        DataArray to the fallback array.
    conversion_arr : string, xarray.DataArray, tuple or float
        Conversion array to pre-scale quantities. If provided, the input food
        balance sheet is first converted using the conversion array, then the
        scaling is applied, and finally the results are converted back to the
        original units using the inverse of the conversion array.
    out_key : string, tuple
        Output datablock path to write results to. If not given, input path is
        overwritten
    datablock : dict, optional
        Dictionary containing data

    Returns
    -------
    data : xarray.Dataarray
        Food balance sheet Dataset with scaled values.
    """

    # Pepare inputs
    data = copy.deepcopy(get_dict(datablock, fbs))

    if conversion_arr is not None:
        if isinstance(conversion_arr, xr.DataArray):
            conversion_arr = conversion_arr.where(
                np.isfinite(conversion_arr), other=1)
            if (conversion_arr == 0).any():
                warnings.warn("Conversion array contains zero values, "
                              "which can lead to inaccurate scaling")
        elif isinstance(conversion_arr, (int, float)):
            conversion_arr = xr.full_like(
                data[element], fill_value=conversion_arr)
        else:
            conversion_arr = get_dict(datablock, conversion_arr)

    else:
        conversion_arr = xr.ones_like(data[element])

    data = data*conversion_arr

    out = copy.deepcopy(data)

    if out_key is None:
        out_key = fbs

    if items is None:
        scaled_items = data.Item.values
        constant = False
    else:
        scaled_items = item_parser(data, items)

    if origin is not None and np.isscalar(origin):
        origin = [origin]

        if np.isscalar(add_to_origin):
            add_to_origin = [add_to_origin]*len(origin)

        if elasticity is None:
            elasticity = [1/len(origin)]*len(origin)

    # Scale input
    if origin is None:
        out = out.fbs.scale_element(
            element=element,
            scale=scale,
            items=scaled_items
        )

    else:
        out = out.fbs.scale_add(
            element_in=element,
            element_out=origin,
            scale=scale,
            items=scaled_items,
            add=add_to_origin,
            elasticity=elasticity
        )

    # If quantities are set to be constant
    if constant:

        delta = out[element] - data[element]

        # Identify non selected items and scaling
        if padding_items is None:
            non_sel_items = np.setdiff1d(data.Item.values, scaled_items)
        else:
            non_sel_items = item_parser(data, padding_items)
        non_sel_scale = (data.sel(Item=non_sel_items)[element].sum(dim="Item")
                         - delta.sum(dim="Item")) \
            / data.sel(Item=non_sel_items)[element].sum(dim="Item")

        # Identify where denominator is zero (non-finite scale)
        non_finite_mask = ~np.isfinite(non_sel_scale)

        # Use multiplicative scaling where finite, no-op (scale=1) where not
        non_sel_scale_finite = non_sel_scale.where(
            np.isfinite(non_sel_scale)).fillna(1.0)

        if origin is None:
            out = out.fbs.scale_element(
                element=element,
                scale=non_sel_scale_finite,
                items=non_sel_items
            )

        else:
            out = out.fbs.scale_add(
                element_in=element,
                element_out=origin,
                scale=non_sel_scale_finite,
                items=non_sel_items,
                add=add_to_origin,
                elasticity=elasticity
            )

        # For non-finite cases (zero original quantity), add delta directly
        # distributed equally across non_sel_items
        if bool(non_finite_mask.any()):
            n_non_sel = len(non_sel_items)
            per_item_additive = (
                (-delta.sum(dim="Item")).where(non_finite_mask).fillna(0)
                / n_non_sel
            )

            sel = {"Item": non_sel_items}

            out[element].loc[sel] = out[element].loc[sel] + per_item_additive
            if origin is not None:
                for elmnt, add_el, elast in zip(origin, add_to_origin, elasticity):
                    out[elmnt].loc[sel] = (
                        out[elmnt].loc[sel]
                        + np.where(add_el, -1, 1) *
                        (-per_item_additive) * elast
                    )

    # If a fallback DataArray is defined, transfer the excess negative
    # quantities to it
    if fallback is not None:
        for orig in origin:
            dif = out[orig].where(out[orig] < 0).fillna(0)
            out[fallback] -= np.where(add_to_fallback, 1, -1)*dif
            out[orig] = out[orig].where(out[orig] > 0, 0)

    # Convert back to original units if conversion array is provided
    conversion_arr = conversion_arr.where(conversion_arr != 0, other=1)
    out = out/conversion_arr

    set_dict(datablock, out_key, out)

    return datablock


@standalone(input_keys=["fbs", "convertion_arr"], return_keys=["out_key"])
def fbs_convert(
    fbs,
    convertion_arr,
    out_key=None,
    datablock=None
):
    """Scales quantities in a food balance sheet using a conversion
    dataarray, dataset, or scaling factor.

    Parameters
    ----------
    fbs : str, xarray.Dataset
        Datablock paths to the food balance sheet datasets or the datasets
        themselves.
    convertion_arr : str, xarray.DataArray, tuple or float
        Datablock path to the conversion array, datablock-key tuple, or the
        array or float itself.
    out_key : str, list
        Datablock key of the resulting dataset to be stored in the datablock.
    datablock : Dict
        Dictionary containing data.

    Returns
    -------
    dict or xarray.Dataset
        - Updated datablock if  a datablock is provided.
        - xarray.Dataset with converted quantities if no datablock is provided.
    """

    # Retrieve target array
    data = get_dict(datablock, fbs)

    # retrieve convertion array
    if isinstance(convertion_arr, xr.DataArray):
        convertion_arr = convertion_arr.where(
            np.isfinite(convertion_arr), other=0)
    else:
        convertion_arr = get_dict(datablock, convertion_arr)

    # If no output key is provided, overwrite original dataset
    if out_key is None:
        out_key = fbs

    out = data*convertion_arr
    set_dict(datablock, out_key, out)

    return datablock


@standalone(["fbs"], ["out_key"])
def SSR(
    fbs,
    items=None,
    per_item=False,
    production="production",
    imports="imports",
    exports="exports",
    out_key=None,
    datablock=None,
):
    """Self-sufficiency ratio

    Self-sufficiency ratio (SSR) or ratios for a list of item imports,
    exports and production quantities.

    Parameters
    ----------
    fbs : xarray.Dataset
        Input Dataset containing an "Item" coordinate and, optionally, a
        "Year" coordinate.
    items : list, optional
        list of items to compute the SSR for from the food Dataset. If no
        list is provided, the SSR is computed for all items.
    per_item : bool, optional
        Whether to return an SSR for each item separately. Default is false
    production : string, optional
        Name of the DataArray containing the production data
    imports : string, optional
        Name of the DataArray containing the imports data
    exports : string, optional
        Name of the DataArray containing the exports data
    datablock : dict, optional
        Dictionary containing the food balance sheet Dataset.

    Returns
    -------
    data : xarray.Dataarray
        Self-sufficiency ratio or ratios for the list of items, one for each
        year of the input food Dataset "Year" coordinate.

    """

    fbs = get_dict(datablock, fbs)

    if items is not None:
        if np.isscalar(items):
            items = [items]
        fbs = fbs.sel(Item=items)

    domestic_use = fbs[production] + fbs[imports] - fbs[exports]

    if per_item:
        ssr = fbs[production] / domestic_use
    else:
        ssr = fbs[production].sum(dim="Item") / domestic_use.sum(dim="Item")

    set_dict(datablock, out_key, ssr)

    return datablock


@standalone(["fbs"], ["out_key"])
def IDR(
    fbs,
    items=None,
    per_item=False,
    imports="imports",
    production="production",
    exports="exports",
    out_key=None,
    datablock=None,
):
    """Import-dependency ratio

    Import-ependency ratio (IDR) or ratios for a list of item imports,
    exports and production quantities.

    Parameters
    ----------
    fbs : xarray.Dataset
        Input Dataset containing an "Item" coordinate and, optionally, a
        "Year" coordinate.
    items : list, optional
        list of items to compute the IDR for from the food Dataset. If no
        list is provided, the IDR is computed for all items.
    per_item : bool, optional
        Whether to return an IDR for each item separately. Default is false.
    imports : string, optional
        Name of the DataArray containing the imports data
    exports : string, optional
        Name of the DataArray containing the exports data
    production : string, optional
        Name of the DataArray containing the production data
    datablock : dict, optional
        Dictionary containing the food balance sheet Dataset.

    Returns
    -------
    data : xarray.Datarray
        Import-dependency ratio or ratios for the list of items, one for
        each year of the input food Dataset "Year" coordinate.
    """

    fbs = get_dict(datablock, fbs)

    if items is not None:
        if np.isscalar(items):
            items = [items]
        fbs = fbs.sel(Item=items)

    domestic_use = fbs[production] + fbs[imports] - fbs[exports]

    if per_item:
        idr = fbs["imports"] / domestic_use
    else:
        idr = fbs["imports"].sum(dim="Item") / domestic_use.sum(dim="Item")

    set_dict(datablock, out_key, idr)

    return datablock


@pipeline_node(["fbs", "conversion_arr"])
def scale_above_threshold(
    fbs,
    scale,
    element,
    threshold=0,
    items=None,
    origin=None,
    add_to_origin=True,
    elasticity=None,
    fallback=None,
    add_to_fallback=True,
    conversion_arr=None,
):
    """Scales excess item quantities in a food balance sheet above a certain
    threshold
    
    Parameters
    ----------
    fbs : xarray.Dataset
        Input food balance sheet Dataset
    scale : float, xarray.DataArray
        Scaling value or array to apply to the excess above the threshold
    element : string
        Name of the DataArray to scale
    threshold : float, xarray.DataArray, optional
        Minimum value for the scaled element. Scaling of item quantities is
        only applied to the excess above this threshold.
    items : list, optional
        List of items to scaled in the food balance sheet. If None, all items
        are scaled.
    origin : string, list, optional
        Names of the DataArrays which will be used as source for the quantity
        changes. Any change to the "element" DataArray will be reflected in
        this DataArray
    add_to_origin : bool, array, optional
        Whether to add or subtract the difference from the respective origins
    elasticity : float, array, optional
        Relative fraction of the total difference to be assigned to each origin
        element. Values are not normalized.
    fallback : string
        Name of the DataArray to use as fallback in case the origin quantities
        fall below zero
    add_to_fallback : bool, optional
        Whether to add or subtract the difference below zero in the origin
        DataArray to the fallback array.
    conversion_arr : string, xarray.DataArray, tuple or float
        Conversion array to pre-scale quantities. If provided, the input food
        balance sheet is first converted using the conversion array, then the
        scaling is applied, and finally the results are converted back to the
        original units using the inverse of the conversion array.
    """

    if conversion_arr is not None:
        if isinstance(conversion_arr, xr.DataArray):
            conversion_arr = conversion_arr.where(
                np.isfinite(conversion_arr), other=1)
            if (conversion_arr == 0).any():
                warnings.warn("Conversion array contains zero values," \
                "which can lead to inaccurate scaling")

        elif isinstance(conversion_arr, (int, float)):
            conversion_arr = xr.full_like(
                fbs[element], fill_value=conversion_arr)
    else:
        conversion_arr = xr.ones_like(fbs[element])

    fbs = fbs*conversion_arr

    if items is not None:
        scaled_items = item_parser(fbs, items)
        sel = {"Item": scaled_items}
    else:
        scaled_items = fbs.Item.values
        sel = {}

    # Calculate the maximum scale threshold that would reduce the sum of the
    # element to the threshold, and apply the input scale relative to this
    max_scale_threshold = (fbs[element].sum(dim="Item") - threshold) \
        / fbs[element].sel(sel).sum(dim="Item")
    
    scale_threshold = max_scale_threshold * scale

    if origin is not None and np.isscalar(origin):
        origin = [origin]

        if np.isscalar(add_to_origin):
            add_to_origin = [add_to_origin]*len(origin)

        if elasticity is None:
            elasticity = [1/len(origin)]*len(origin)

    # Scale input
    if origin is None:
        out = fbs.fbs.scale_element(
            element=element,
            scale=1-scale_threshold,
            items=scaled_items
        )

    else:
        out = fbs.fbs.scale_add(
            element_in=element,
            element_out=origin,
            scale=1-scale_threshold,
            items=scaled_items,
            add=add_to_origin,
            elasticity=elasticity
        )

    # If a fallback DataArray is defined, transfer the excess negative
    # quantities to it
    if fallback is not None and origin is not None:
        for orig in origin:
            dif = out[orig].where(out[orig] < 0).fillna(0)
            out[fallback] -= np.where(add_to_fallback, 1, -1)*dif
            out[orig] = out[orig].where(out[orig] > 0, 0)

    # Convert back to original units if conversion array is provided
    conversion_arr = conversion_arr.where(conversion_arr != 0, other=1)
    out = out/conversion_arr

    return out
