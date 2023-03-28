""" Food supply module.
"""

import numpy as np
import xarray as xr
import os
import copy

import matplotlib.pyplot as plt
import warnings

from ..utils.list_tools import tolist

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['FAOSTAT', 'EAT_Lancet', 'RDA_eatwell', 'Nutrients', "Nutrients_FAOSTAT"]

FAOSTAT_elements = ['production',
                    'imports',
                    'exports',
                    'stock',
                    'feed',
                    'seed',
                    'losses',
                    'processing',
                    'residual',
                    'tourist',
                    'domestic',
                    'other',
                    'food',
                    ]

def FoodSupply(items, years, quantities, regions=None, elements=None, long_format=True):
    """ Food Supply style dataset constructor
     
    Parameters
    ----------
    items : (ni,) array_like
        The Item identifying ID or strings for which coordinates will be
        created.
    years : years : (ny,) array_like
        The year values for which coordinates will be created.
    quantities : ([ne], ni, ny, [nr]) ndarray
        Array containing the food quantity for each combination of `Item`,
        `Year` and, optionally `Region`.
    regions : (nr,) array_like, optional
        The region identifying ID or strings for which coordinates will be
        created.
    long_format : bool
        Boolean flag to interpret data in long or wide format
    elemements : (ne,) array_like, optional
        Array with element name strings. If `elements` is provided, a dataset
        is created for each element in `elements` with the quantities being each
        of the sub-arrays indexed by the first coordinate of the input array.

    Returns
    -------
    data : xarray.Dataset
        Food Supply dataset containing the food quantity for each `Item`, `Year`
        and `Region` with one dataarray per element in `elements`.
    """

    # if the input has a single element, proceed with long format
    if np.isscalar(quantities):
        long_format = True

    quantities = np.array(quantities)

    # Identify unique values in coordinates
    _items = np.unique(items)
    _years = np.unique(years)
    coords = {"Item" : _items,
              "Year" : _years,} 

    # find positions in output array to organize data
    ii = [np.searchsorted(_items, items), np.searchsorted(_years, years)]
    size = (len(_items), len(_years))

    # If regions and are provided, add the coordinate information 
    if regions is not None:
        _regions = np.unique(regions)
        ii.append(np.searchsorted(_regions, regions))
        size = size + (len(_regions),)
        coords["Region"] = _regions

    # Create empty dataset
    data = xr.Dataset(coords = coords)

    if long_format:
        # dataset, quantities
        ndims = 2
    else:
        # dataset, coords
        ndims = len(coords)+1
    
    # make sure the long format has the right number of dimensions
    while len(quantities.shape) < ndims:
        quantities = np.expand_dims(quantities, axis=0)

    # If no elements names are given, then create generic ones,
    # one for each dataset
    if elements is None:
        elements = [f"Quantity {id}" for id in range(quantities.shape[0])]

    # Else, if a single string is given, transform to list. If doesn't match
    # the number of datasets created above, xarray will return an error.
    elif isinstance(elements, str):
        elements = [elements]

    if long_format:
        # Create a datasets, one at a time
        for ie, element in enumerate(elements):
            values = np.zeros(size)*np.nan
            values[tuple(ii)] = quantities[ie]
            data[element] = (coords, values)

    else:
        quantities = quantities[:, ii[0]]
        if len(quantities.shape) < ndims:
            quantities = np.expand_dims(quantities, axis=0)

        quantities = quantities[:, :, ii[1]]
        if len(quantities.shape) < ndims:
            quantities = np.expand_dims(quantities, axis=0)

        if regions is not None:
            quantities = quantities[..., ii[2]]
        # Create a datasets, one at a time
        for ie, element in enumerate(elements):
            values = quantities[ie]
            data[element] = (coords, values)

    return data

def scale_element(food, element, scale, items=None):
    """ TO-DO DOCSTRINGS"""

    if np.isscalar(items):
        items = [items]

    input_item_list = food.Item.values.tolist()

    if items is None or np.sort(items) is np.sort(input_item_list):
        items = food.Item.values

    sel = {"Item":items}

    out = copy.deepcopy(food)

    # Scale items
    out[element].loc[sel] *= scale

    return out

def scale_food(food, scale, origin, items=None, constant=False, fallback=None):
    """Scales Food Supply style `food` quantities according to defined
    constraints

    Parameters
    ----------
    food : xarray.Dataset
        Input Dataset containing at least the `production`, `imports`, `exports`
        and `food` Dataarrays
    scale : float, float array_like or xarray.Dataarray
        Values to scale the `food` quantities.
    origin : str, one of "production", "imports", "exports"
        Dataset used to act as the source of the increased or decreased `food`
        quantities.
    items : list of int or list of str, optional
        List of items to be scaled. If not provided, all items are scaled and
        the `constant` boolean is ignored with a warning.
    constant : bool, optional
        If True, the sum of the `food` dataarray quantities is kept constant by
        scaling the non selected items by the appropriate scaling factor.
    fallback : str, optional
        In case the an `origin` item quantity results in a negative value, it is
        set to zero and the difference added or subtracted to the `fallback` Dataset

    Returns
    -------
    out : xarray.Dataset
        FAOSTAT formatted Food Supply dataset with scaled quantities.

    """

    if np.isscalar(items):
        items = [items]

    input_item_list = food.Item.values.tolist()

    if np.isscalar(input_item_list):
        input_item_list = [input_item_list]
        sel = {}
        non_sel = {}
        if constant:
            warnings.warn("Constant set to true but input only has one item.")
            constant = False
    else:
        sel = {"Item":items}

    # If no items are provided, we scale all of them.
    if items is None or np.sort(items) is np.sort(input_item_list):
        items = food.Item.values
        if constant:
            warnings.warn("Cannot keep food constant when scaling all items.")
            constant = False

    # Check that origin is within the acceptable values.
    # If exports, shift the sign of adjustment
    assert origin in ["production", "imports", "exports"], "'origin' must be one of 'production', 'imports', 'exports'."

    # Create a deepcopy to modify
    out = copy.deepcopy(food)

    # Scale items
    out["food"].loc[sel] *= scale

    # Compute differente needed to be added to origin.
    # If origin is exports, then set it to be negative.
    delta = out["food"].loc[sel] - food["food"].loc[sel]

    if origin == "exports":
        out[origin].loc[sel] -= delta
    else:
        out[origin].loc[sel] += delta

    # If constant, total food is kept constant, at the expense of non-selected items
    if constant:

        nonsel = out.drop_sel(Item=items)
        nonsel_items = nonsel.Item.values
        non_sel = {"Item":nonsel_items}

        # Compute scale for non-selected items
        nonsel_scale = (nonsel["food"].sum(dim="Item") - delta.sum(dim="Item")) / nonsel["food"].sum(dim="Item")
        if np.any(nonsel_scale < 0):
            warnings.warn("Additional consumption cannot be compensated by reduction of non-selected items")

        out["food"].loc[non_sel] *= nonsel_scale
        nonsel_delta = out["food"].loc[non_sel] - food["food"].loc[non_sel]
        out[origin].loc[non_sel] += nonsel_delta

        delta_fallback = out[origin].where(out[origin] < 0).fillna(0)

        if fallback == "exports":
            out[fallback] -= delta_fallback
        else:
            out[fallback] += delta_fallback

        out[origin] = out[origin].where(out[origin] > 0, 0)

    return out

def plot_bars(food, show="Item", ax=None, colors=None, labels=None, **kwargs):
    """Horizontal dissagregated bar plot

    Produces a horizontal bar the size of the total quantity summed along the
    coordinates not specified by `show`, and coloured segments to indicate
    the contribution of the each item along the specified `show` coordinate.
    Bars for each dataarray of the dataset have their starting points on the end
    of the previous bar, with `production` and `imports` placed on top, and the
    remaining bars in reverse with `food` placed at the bottom.

    Parameters
    ----------
    food : xarray.Dataset
        Input Dataset containing at least: a `production`, `imports`, `exports`
        and `food` Dataarray
    show : str, optional
        Name of the coordinate to dissagregate when filling the horizontal
        bar. The quantities are summed along the remaining coordinates.
        If the coordinate does not exist in the input, all
        coordinates are summed and a plot with a single color is returned.
    ax : matplotlib.pyplot.artist, optional
        Axes on which to draw the plot. If not provided, a new artist is
        created.
    colors : list of str, optional
        String list containing the colors for each of the elements in the "show"
        coordinate.
        If not defined, a color list is generated from the standard cycling.
    label : list of str, optional
        String list containing the labels for the legend of the elements in the
        "show" coordinate
    **kwargs : dict
        Style options to be passed on to the actual plot function, such as
        linewidth, alpha, etc.

    Returns
    -------
        ax : matplotlib axes instance
    """

    if ax is None:
        f, ax = plt.subplots(**kwargs)

    # Make sure only FAOSTAT food elements are present
    input_elements = list(food.keys())
    plot_elements = ["production", "imports", "exports", "food"]

    for element in plot_elements:
        if element not in input_elements:
            elements.remove(element)

    for element in input_elements:
        if element not in plot_elements and element in FAOSTAT_elements:
            plot_elements.insert(-1, element)

    len_elements = len(plot_elements)

    # Define dimensions to sum over
    bar_dims = list(food.dims)
    if show in bar_dims:
        bar_dims.remove(show)
        size_show = food.sizes[show]
    else:
        size_show = 1

    # Make sure NaN and inf do not interfere
    food = food.fillna(0)
    food = food.where(np.isfinite(food), other=0)

    food_sum = food.sum(dim=bar_dims)

    # If colors are not defined, generate a list from the standard cycling
    if colors is None:
        colors = [f"C{ic}" for ic in range(size_show)]

    # If labels are not defined, generate a list from the dimensions
    if labels is None:
        labels = np.repeat("", len(colors))

    # Plot the production and imports first
    cumul = 0
    for ie, element in enumerate(["production", "imports"]):
        ax.hlines(ie, 0, cumul, color="k", alpha=0.2, linestyle="dashed", linewidth=0.5)
        if size_show == 1:
            ax.barh(ie, left = cumul, width=food_sum[element], color=colors[0])
            cumul +=food_sum[element]
        else:
            for ii, val in enumerate(food_sum[element]):
                ax.barh(ie, left = cumul, width=val, color=colors[ii], label=labels[ii])
                cumul += val

    # Then the rest of elements in reverse to keep dimension ordering
    cumul = 0
    for ie, element in enumerate(reversed(plot_elements[2:])):
        ax.hlines(len_elements-1 - ie, 0, cumul, color="k", alpha=0.2, linestyle="dashed", linewidth=0.5)
        if size_show == 1:
            ax.barh(len_elements-1 - ie, left = cumul, width=food_sum[element], color=colors[0])
            cumul +=food_sum[element]
        else:
            for ii, val in enumerate(food_sum[element]):
                ax.barh(len_elements-1 - ie, left = cumul, width=val, color=colors[ii], label=labels[ii])
                cumul += val

    # Plot decorations
    ax.set_yticks(np.arange(len_elements), labels=plot_elements)
    ax.tick_params(axis="x",direction="in", pad=-12)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_ylim(len_elements+1,-1)

    # Unique labels
    if labels[0] != "":
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), fontsize=6)

    return ax

def plot_years(food, show="Item", ax=None, colors=None, label=None, **kwargs):
    """ Fill plot with quantities at each year value

    Produces a vertical fill plot with quantities for each year on the "Year"
    coordinate of the input dataset in the horizontal axis. If the "show"
    coordinate exists, then the vertical fill plot is a stack of the sums of
    the other coordinates at that year for each item in the "show" coordinate.

    Parameters
    ----------
    food : xarray.Dataarray
        Input Dataarray containing a "Year" coordinate and optionally, a

    show : str, optional
        Name of the coordinate to dissagregate when filling the vertical
        plot. The quantities are summed along the remaining coordinates.
        If the coordinate is not provided or does not exist in the input, all
        coordinates are summed and a plot with a single fill curve is returned.
    ax : matplotlib.pyplot.artist, optional
        Axes on which to draw the plot. If not provided, a new artist is
        created.
    colors : list of str, optional
        String list containing the colors for each of the elements in the "show"
        coordinate.
        If not defined, a color list is generated from the standard cycling.
    label : list of str, optional
        String list containing the labels for the legend of the elements in the
        "show" coordinate
    **kwargs : dict
        Style options to be passed on to the actual plot function, such as
        linewidth, alpha, etc.

    Returns
    -------
        ax : matplotlib axes instance
    """

    # If no years are found in the dimensions, raise an exception
    sum_dims = list(food.dims)
    if "Year" not in sum_dims:
        raise TypeError("'Year' dimension not found in array data")

    # Define the cumsum and sum dimentions and check for one element dimensions
    sum_dims.remove("Year")
    if ax is None:
        f, ax = plt.subplots(1, **kwargs)

    if show in sum_dims:
        sum_dims.remove(show)
        size_cumsum = food.sizes[show]
        cumsum = food.cumsum(dim=show).transpose(show, ...)
    else:
        size_cumsum = 1
        cumsum = food

    # Collapse remaining dimensions
    cumsum = cumsum.sum(dim=sum_dims)
    years = food.Year.values

    # If colors are not defined, generate a list from the standard cycling
    if colors is None:
        colors = [f"C{ic}" for ic in range(size_cumsum)]

    # Plot
    if size_cumsum == 1:
        ax.fill_between(years, cumsum, color=colors[0], alpha=0.5)
        ax.plot(years, cumsum, color=colors[0], linewidth=0.5, label=label)
    else:
        for id in reversed(range(size_cumsum)):
            ax.fill_between(years, cumsum[id], color=colors[id], alpha=0.5)
            ax.plot(years, cumsum[id], color=colors[id], linewidth=0.5, label=label)

    ax.set_xlim(years.min(), years.max())

    return ax

def SSR(food, items=None, per_item=False):
    """Self-sufficiency ratio

    Self-sufficiency ratio (SSR) or ratios for a list of item imports, exports
    and production quantities.

    Parameters
    ----------
    food : xarray.Dataset
        Input Dataset containing an "Item" coordinate and, optionally, a "Year"
        coordinate.
    items : list, optional
        list of items to compute the SSR for from the food Dataset. If no list
        is provided, the SSR is computed for all items.
    per_item : bool, optional
        Whether to return an SSR for each item separately. Default is false

    Returns
    -------
    data : xarray.Dataarray
        Self-sufficiency ratio or ratios for the list of items, one for each
        year of the input food Dataset "Year" coordinate.

    """

    if items is not None:
        food = food.sel(Item=items)

    if per_item:
        return food["production"] / (food["production"] + food["imports"] - food["exports"])

    return food["production"].sum(dim="Item") / (food["production"] + food["imports"] - food["exports"]).sum(dim="Item")

def IDR(food, items=None, per_item=False):
    """Import-dependency ratio

    Import-ependency ratio (IDR) or ratios for a list of item imports, exports
    and production quantities.

    Parameters
    ----------
    food : xarray.Dataset
        Input Dataset containing an "Item" coordinate and, optionally, a "Year"
        coordinate.
    items : list, optional
        list of items to compute the IDR for from the food Dataset. If no list
        is provided, the IDR is computed for all items.
    per_item : bool, optional
        Whether to return an IDR for each item separately. Default is false.

    Returns
    -------
    data : xarray.Datarray
        Import-dependency ratio or ratios for the list of items, one for each
        year of the input food Dataset "Year" coordinate.

    """

    if items is not None:
        food = food.sel(Item=items)

    if per_item:
        return food["imports"] / (food["production"] + food["imports"] - food["exports"])

    return food["imports"].sum(dim="Item") / (food["production"] + food["imports"] - food["exports"]).sum(dim="Item")

def __getattr__(name):
    if name not in available:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}.")

    _data_file = f'{data_dir}{name}.nc'

    # If the file contains more than a single dataarray, then it will try
    # to load it as a dataset
    try:
        data = xr.open_dataarray(_data_file)
    except ValueError:
        data = xr.open_dataset(_data_file)
    return data
