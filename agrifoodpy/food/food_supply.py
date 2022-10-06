import numpy as np
import xarray as xr
import os
import copy

import matplotlib.pyplot as plt
import warnings

from ..utils.list_tools import tolist

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['FAOSTAT', 'EAT_Lancet', 'RDA_eatwell', 'Nutrients']

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

def FoodSupply(items, years, quantities, regions=None, elements=None):

    _years = np.unique(years)
    _items = np.unique(items)

    size = (len(_years), len(_items))

    ii = [np.searchsorted(_years, years), np.searchsorted(_items, items)]

    coords = {"Year" : _years,
              "Item" : _items}

    if regions is not None:
        _regions = np.unique(regions)
        ii.append(np.searchsorted(_regions, regions))
        size = size + (len(_regions),)
        coords["Region"] = _regions

    if elements is not None:
        _elements = np.unique(elements)
        ii.append(np.searchsorted(_elements, elements))
        coords["Element"] = _elements
        size = size + (len(_elements),)

    values = np.zeros(size)*np.nan

    values[tuple(ii)] = quantities

    data = xr.Dataset(data_vars = dict(value=(coords.keys(), values)), coords = coords)

    return data

def scale_food(food, scale, origin, items=None, constant=False, fallback=None):

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

def plot_bars(food, show="Item", ax=None, colors=None, **kwargs):

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

    food_sum = food.sum(dim=bar_dims)

    # If colors are not defined, generate a list from the standard cycling
    if colors is None:
        colors = [f"C{ic}" for ic in range(size_show)]

    # Plot the production and imports first
    cumul = 0
    for ie, element in enumerate(["production", "imports"]):
        if size_show == 1:
            ax.barh(ie, left = cumul, width=food_sum[element], color=colors[0])
            cumul +=food_sum[element]
        else:
            for ii, val in enumerate(food_sum[element]):
                ax.barh(ie, left = cumul, width=val, color=colors[ii])
                cumul += val

    # Then the rest of elements in reverse to keep dimension ordering
    cumul = 0
    for ie, element in enumerate(reversed(plot_elements[2:])):
        if size_show == 1:
            ax.barh(len_elements-1 - ie, left = cumul, width=food_sum[element], color=colors[0])
            cumul +=food_sum[element]
        else:
            for ii, val in enumerate(food_sum[element]):
                ax.barh(len_elements-1 - ie, left = cumul, width=val, color=colors[ii])
                cumul += val

    # Plot decorations
    ax.set_yticks(np.arange(len_elements), labels=plot_elements)
    ax.set_yticks(ax.get_yticks())
    ax.tick_params(axis="x",direction="in", pad=-12)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_ylim(len_elements+1,-1)

    return ax

def plot_years(food, show="Item", ax=None, colors=None, **kwargs):

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
        ax.fill_between(years, cumsum, alpha=0.5)
        ax.plot(years, cumsum, color=colors[0], linewidth=0.5)
    else:
        for id in reversed(range(size_cumsum)):
            ax.fill_between(years, cumsum[id], alpha=0.5)
            ax.plot(years, cumsum[id], color=colors[id], linewidth=0.5)

    return ax

def SSR(food, items=None, per_item=False):

    if items is not None:
        food = food.sel(Item=items)

    if per_item:
        return food["production"] / (food["production"] + food["imports"] - food["exports"])

    return food["production"].sum(dim="Item") / (food["production"] + food["imports"] - food["exports"]).sum(dim="Item")

def IDR(food, items=None, per_item=False):

    if items is not None:
        food = food.sel(Item=items)

    if per_item:
        return food["imports"] / (food["production"] + food["imports"] - food["exports"])

    return food["imports"].sum(dim="Item") / (food["production"] + food["imports"] - food["exports"]).sum(dim="Item")

def __getattr__(name):
    if name not in available:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}.")

    _data_file = f'{data_dir}{name}.nc'
    data = xr.open_dataset(_data_file)

    return data
