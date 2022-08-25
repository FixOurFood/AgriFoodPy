import numpy as np
import xarray as xr
import os
import copy

import matplotlib.pyplot as plt
import collections
import warnings

from ..utils.list_tools import tolist

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['FAOSTAT']

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

    # If no items are provided, we scale all of them.
    if items is None or np.sort(items) is np.sort(food.Item.values):
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
    out["food"].loc[items] *= scale

    # Compute differente needed to be added to origin.
    # If origin is exports, then set it to be negative.
    delta = out["food"].loc[items] - food["food"].loc[items]

    if origin == "exports":
        out[origin].loc[items] -= delta
    else:
        out[origin].loc[items] += delta

    # If constant, total food is kept constant, at the expense of non-selected items
    if constant:
        nonsel = out.drop_sel(Item=items)
        nonsel_items = nonsel.Item.values

        # Compute scale for non-selected items
        nonsel_scale = (nonsel["food"].sum() - delta.sum()) / nonsel["food"].sum()
        if nonsel_scale < 0:
            print(nonsel_scale)
            warnings.warn("Additional consumption cannot be compensated by reduction of non-selected items")

        out["food"].loc[nonsel_items] *= nonsel_scale
        nonsel_delta = out["food"].loc[nonsel_items] - food["food"].loc[nonsel_items]
        out[origin].loc[nonsel_items] += nonsel_delta

        if fallback == "exports":
            out[fallback].loc[out[origin] < 0] -= out[origin].loc[out[origin] < 0]
        else:
            out[fallback].loc[out[origin] < 0] += out[origin].loc[out[origin] < 0]

        out[origin] = out[origin].where(out[origin] > 0, 0)

    return out

def plot_food(food, items=None, colors=None, sharex=False):

    # Check if a list of food xarrays was provided. If single one, convert to list
    to_plot = food
    if not isinstance(food, collections.abc.Iterable):
        to_plot = (food, )

    fig, axs = plt.subplots(len(to_plot), figsize=(10,3*len(to_plot)), sharex=sharex)
    plt.subplots_adjust(hspace=0)

    for ax, unit in zip(axs, to_plot):

        # If not list of items is provided, plot all the items
        if items is None:
            items = unit.Item.values

        # If colors are not defined, generate a list from the standard cycling
        if colors is None:
            colors = [f"C{ic}" for ic in range(len(items))]

        elements = list(unit.keys())

        # Plot the production and imports first
        cumul = 0
        for ie, element in enumerate(["production", "imports"]):
            for ii, item in enumerate(items):
                val = np.sum(unit[element].sel(Item=item))
                ax.barh(ie, left = cumul, width=val, color=colors[ii])
                cumul += val

        subs = copy.deepcopy(elements)
        subs.remove("imports")
        subs.remove("production")

        # Then the rest of items
        cumul = 0
        for ie, element in enumerate(reversed(subs)):
            for ii, item in enumerate(items):
                val = np.sum(unit[element].sel(Item=item))
                ax.barh(9-ie, left = cumul, width=val, color=colors[ii])
                cumul += val

        ax.set_yticks(np.arange(len(elements)))
        ax.set_xticks(ax.get_xticks()[1:-1])
        ax.tick_params(axis="x",direction="in", pad=-12)
        ax.set_yticklabels(labels=elements)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_ylim(len(elements)+1,-1)

    return fig, axs

def SSR(food, items=None, per_item=False):

    # Should per_year and per_region be also added?

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
