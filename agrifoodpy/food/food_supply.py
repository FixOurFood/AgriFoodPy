""" Food supply module.
"""

import numpy as np
import xarray as xr
import os
import copy

import matplotlib.pyplot as plt

from ..utils.scaling import logistic_scale, linear_scale

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['FAOSTAT', 'EAT_Lancet', 'RDA_eatwell', 'Nutrients', "Nutrients_FAOSTAT"]

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
    fbs : xarray.Dataset
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
    fbs = xr.Dataset(coords = coords)

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
            fbs[element] = (coords, values)

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
            fbs[element] = (coords, values)

    return fbs

@xr.register_dataset_accessor("fbs")
class FoodBalanceSheet:
    def __init__(self, xarray_obj):
        self._validate(xarray_obj)
        self._obj = xarray_obj

    @staticmethod
    def _validate(obj):
        """Validate fbs xarray, checking it is a DataSet and has the minimum set
        of arrays
        """
        if not isinstance(obj, xr.Dataset):
            raise TypeError("Food Balance Sheet must be an xarray.DataSet")

        required_data_arrays = ["production", "imports", "exports", "food"]
        missing_data_arrays = []

        for data_array_name in required_data_arrays:
            if data_array_name not in obj.data_vars:
                missing_data_arrays.append(data_array_name)

        if missing_data_arrays:
            raise AttributeError(f"Missing data arrays: {missing_data_arrays}")


    def add_items(self, items, copy_from=None, labels=None):
        """Extends the item list of a food balance sheet according to the
        defined input item list

        Parameters
        ----------
        fbs : xarray.Dataset
            Input food balance sheet Dataset
        items : list, int, string
            list of item names to be added to the data
        copy_from : list, int, string, optional
            If provided, this is the list of items already on the food balance
            sheet to copy data from.
        labels : dict 
            Dictionary containing the new label for the items matched to its
            corresponding label coordinate.
        
        Returns
        -------
        fbs : xarray.Dataset, xarray.DataArray 
            FAOSTAT formatted Food Supply dataset with new items added.
        """

        fbs = self._obj

        items = np.unique(items)
        
        new_items = xr.DataArray(data = np.ones(len(items)),
                                coords = {"Item":items})

        if copy_from is not None:
            fbs_pivot = fbs.sel(Item=copy_from)
            fbs_pivot["Item"] = items
            new_fbs = fbs_pivot*new_items
            
        else:
            new_items *= np.nan
            new_fbs = fbs.isel(Item=0)*new_items
            
            if labels is not None:
                for key, item in labels.items():
                    new_fbs[key] = item
            
        # Concatenate to input array
        concat_fbs = xr.concat([fbs, new_fbs], dim="Item") 
            
        return concat_fbs

    def add_years(self, years, projection="empty"):
        """Extends the year range of a food balance sheet according to the defined
        maximum year

        Parameters
        ----------
        fbs : xarray.Dataset
            Input food balance sheet Dataset
        years : list, int
            list of years to be added to the data
        projection : string or array_like
            Projection mode. If "constant", the last year of the input food
            balance sheet is copied to every new year. If "empty", values are
            initialized and set to zero. If a float array is given, these are used
            to populate the new year using a scaling of the last year of the array

        Returns
        -------
        fbs : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with new years added.
        """

        fbs = self._obj

        years = np.unique(years)
        
        if projection == "empty":
            data = np.zeros(len(years))
        elif projection == "constant":
            data = np.ones(len(years))
        else:
            data = np.ones(len(years)) * projection
        
        new_years = xr.DataArray(data=data,
                                    coords = {"Year":years})

        # Select last year as pivot
        fbs_pivot = fbs.isel(Year=-1)
        
        # Create DS or DA by multiplying along last value
        new_fbs = fbs_pivot*new_years
        
        # Concatenate to input array
        concat_fbs = xr.concat([fbs, new_fbs], dim="Year") 
            
        return concat_fbs

    def add_regions(self, regions, copy_from=None, labels=None):
        """Extends the region list of a food balance sheet according to the defined
        input region list

        Parameters
        ----------
        fbs : xarray.Dataset
            Input food balance sheet Dataset
        new_regions : list, int, string
            list of region names to be added to the data
        copy_from : list, int, string
            If provided, this is the list of regions already on the food balance sheet
            to copy data from.
        labels : dict 
            Dictionary containing the new label for the regions matched to its
            corresponding label coordinate.
        
        Returns
        -------
        fbs : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with new regions added.
        """
        
        fbs = self._obj

        regions = np.unique(regions)
        
        new_regions = xr.DataArray(data = np.ones(len(regions)),
                                coords = {"Region":regions})

        if copy_from is not None:
            fbs_pivot = fbs.sel(Region=copy_from)
            fbs_pivot["Region"] = regions
            new_fbs = fbs_pivot*new_regions
            
        else:
            new_regions *= np.nan
            new_fbs = fbs.isel(Region=0)*new_regions
            
            if labels is not None:
                for key, item in labels.items():
                    new_fbs[key] = item
            
        # Concatenate to input array
        concat_fbs = xr.concat([fbs, new_fbs], dim="Region") 
            
        return concat_fbs
    
    def group_sum(self, coordinate, new_name=None):
        """Sums quantities over items of a equal group labels and, optionally,
        renames the groups label coordinate.

        Parameters
        ----------
        fbs : xarray.Dataset
            Input food balance sheet Dataset
        coordinate : string
            Coordinate name to group items and sum over them 
        new_name : string, optional 
            New name for the collapsed coordinate
        

        Returns
        -------
        fbs : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with new coordinate base.
        """
        
        fbs = self._obj

        grouped_fbs = fbs.groupby(coordinate).sum()

        if new_name is not None:
            grouped_fbs = grouped_fbs.rename({coordinate:new_name})

        return grouped_fbs

    def scale_element(self, element, scale, items=None):
        """Scales list of items from an element in a food balance sheet like
        DataSet.

            Parameters
        ----------
        fbs : xarray.Dataset
            Input DataSet with FAOSTAT like elements
        scale : float, float array_like or xarray.Dataarray
            Scaling quantities for the element DataArray
        element_in : str
            Element DataArray to be scaled
        element_out : str
            Destination element DataArray to which the difference is added to
        items : list of int or list of str, optional
            List of items to be scaled. If not provided, all items are scaled.
            
        Returns
        -------
        out : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with scaled quantities.
        
        """

        fbs = self._obj

        if np.isscalar(items):
            items = [items]

        input_item_list = fbs.Item.values.tolist()

        # If no item list provided, or list is all the items of the fbs
        if items is None or np.sort(items) is np.sort(input_item_list):
            items = fbs.Item.values

        # Create copy to return
        out = copy.deepcopy(fbs)

        # Scale items
        sel = {"Item":items}
        out[element].loc[sel] = out[element].loc[sel] * scale

        return out

    def scale_add(self, element_in, element_out, scale, items=None, add=True):
        """Scales item quantities of an element and adds the difference to another
        element DataArray
        
        Parameters
        ----------
        fbs : xarray.Dataset

        scale : float, float array_like or xarray.Dataarray
            Scaling quantities for the element DataArray
        element_in : str
            Element DataArray to be scaled
        element_out : str
            Destination element DataArray to which the difference is added to
        items : list of int or list of str, optional
            List of items to be scaled. If not provided, all items are scaled.
            
        Returns
        -------
        out : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with scaled quantities.

        """

        fbs = self._obj

        out = self.scale_element(element_in, scale, items)
        dif = fbs[element_in].fillna(0) - out[element_in].fillna(0)

        out[element_out] += np.where(add, -1, 1)*dif
        
        return out

    def SSR(self, items=None, per_item=False):
        """Self-sufficiency ratio

        Self-sufficiency ratio (SSR) or ratios for a list of item imports, exports
        and production quantities.

        Parameters
        ----------
        fbs : xarray.Dataset
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

        fbs = self._obj

        if items is not None:
            if np.isscalar(items):
                items = [items]
            fbs = fbs.sel(Item=items)

        if per_item:
            return fbs["production"] / (fbs["production"] + fbs["imports"] - fbs["exports"])

        return fbs["production"].sum(dim="Item") / (fbs["production"] + fbs["imports"] - fbs["exports"]).sum(dim="Item")

    def IDR(self, items=None, per_item=False):
        """Import-dependency ratio

        Import-ependency ratio (IDR) or ratios for a list of item imports, exports
        and production quantities.

        Parameters
        ----------
        fbs : xarray.Dataset
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

        fbs = self._obj

        if items is not None:
            if np.isscalar(items):
                items = [items]
            fbs = fbs.sel(Item=items)

        if per_item:
            return fbs["imports"] / (fbs["production"] + fbs["imports"] - fbs["exports"])

        return fbs["imports"].sum(dim="Item") / (fbs["production"] + fbs["imports"] - fbs["exports"]).sum(dim="Item")

    def plot_bars(self, show="Item", elements=None, inverted_elements=None,
                  ax=None, colors=None, labels=None, **kwargs):

        fbs = self._obj

        if ax is None:
            f, ax = plt.subplots(**kwargs)

        if elements is None:
            elements = list(fbs.keys())
            plot_elements = elements

        len_elements = len(elements)

        # Define dimensions to sum over
        bar_dims = list(fbs.dims)
        if show in bar_dims:
            bar_dims.remove(show)
            size_show = fbs.sizes[show]
        else:
            size_show = 1

        # Make sure NaN and inf do not interfere
        fbs = fbs.fillna(0)
        fbs = fbs.where(np.isfinite(fbs), other=0)

        food_sum = fbs.sum(dim=bar_dims)

        # If colors are not defined, generate a list from the standard cycling
        if colors is None:
            colors = [f"C{ic}" for ic in range(size_show)]

        # If labels are not defined, generate a list from the dimensions
        if labels is None:
            labels = fbs[show].values

        # Plot non inverted elements first
        cumul = 0
        for ie, element in enumerate(elements):
            ax.hlines(ie, 0, cumul, color="k", alpha=0.2, linestyle="dashed",
                    linewidth=0.5)
            if size_show == 1:
                ax.barh(ie, left = cumul, width=food_sum[element], color=colors[0])
                cumul +=food_sum[element]
            else:
                for ii, val in enumerate(food_sum[element]):
                    ax.barh(ie, left = cumul, width=val, color=colors[ii],
                            label=labels[ii])
                    cumul += val

        # Then the inverted elements
        if inverted_elements is not None:

            len_elements += len(inverted_elements)
            plot_elements = np.concatenate([elements, inverted_elements])

            cumul = 0
            for ie, element in enumerate(reversed(inverted_elements)):
                ax.hlines(len_elements-1 - ie, 0, cumul, color="k", alpha=0.2,
                        linestyle="dashed", linewidth=0.5)
                if size_show == 1:
                    ax.barh(len_elements-1 - ie, left = cumul, width=food_sum[element],
                            color=colors[0])
                    cumul +=food_sum[element]
                else:
                    for ii, val in enumerate(food_sum[element]):
                        ax.barh(len_elements-1 - ie, left = cumul, width=val,
                                color=colors[ii], label=labels[ii])
                        cumul += val

        # Plot decorations
        ax.set_yticks(np.arange(len_elements), labels=plot_elements)
        ax.tick_params(axis="x",direction="in", pad=-12)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_ylim(len_elements+1,-1)

        # Unique labels
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), fontsize=6)

        return ax

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
