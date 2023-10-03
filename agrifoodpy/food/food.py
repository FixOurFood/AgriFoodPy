""" Food supply module.

The Food module provides the FoodBalanceSheet and FoodElementSheet accessor
classes to manipulate and analyse Food data stored in xarray.Dataset and 
xarray.DataArray formats, respectively.

It also provides a constructor style function which allows the creation of a
FoodBalanceSheet or FoodElementSheet style xarray primitive.
"""

import numpy as np
import xarray as xr
import copy

from agrifoodpy.array_accessor import _XarrayAccessorBase

import matplotlib.pyplot as plt

def FoodSupply(items, years, quantities, regions=None, elements=None,
               long_format=True):
    """ Food Supply style dataset constructor

    Constructs a food balance sheet style xarray.Dataset or xarray.DataArray for
    a given list of items, years and regions, and an array data shaped
    accordingly.  
     
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
    elements : (ne,) array_like, optional
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

        # required_data_arrays = ["production", "imports", "exports", "food"]
        # missing_data_arrays = []

        # for data_array_name in required_data_arrays:
        #     if data_array_name not in obj.data_vars:
        #         missing_data_arrays.append(data_array_name)

        # if missing_data_arrays:
        #     raise AttributeError(f"Missing data arrays: {missing_data_arrays}")


    def add_items(self, items, copy_from=None):
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
        
        Returns
        -------
        fbs : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with new items added.
        """

        fbs = self._obj

        # Check for duplicates
        indexes = np.unique(items, return_index=True)[1]
        items = [items[index] for index in sorted(indexes)] #issues with np.unique
        
        new_items = xr.DataArray(data = np.ones(len(items)),
                                coords = {"Item":items})

        if copy_from is not None:
            fbs_pivot = fbs.sel(Item=copy_from)
            fbs_pivot["Item"] = items
            new_fbs = fbs_pivot*new_items
            
        else:
            new_items *= np.nan
            new_fbs = fbs.isel(Item=0)*new_items
            
        # Concatenate to input array
        concat_fbs = xr.concat([fbs, new_fbs], dim="Item") 
            
        return concat_fbs

    def add_years(self, years, projection="empty"):
        """Extends the year range of a food balance sheet according to the
        defined maximum year

        Parameters
        ----------
        fbs : xarray.Dataset
            Input food balance sheet Dataset
        years : list, int
            list of years to be added to the data
        projection : string or array_like
            Projection mode. If "constant", the last year of the input food
            balance sheet is copied to every new year. If "empty", values are
            initialized and set to zero. If a float array is given, these are
            used to populate the new year using a scaling of the last year of
            the array

        Returns
        -------
        fbs : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with new years added.
        """

        fbs = self._obj

        indexes = np.unique(years, return_index=True)[1]
        years = [years[index] for index in sorted(indexes)]
        
        if projection == "empty":
            data = np.zeros(len(years))*np.nan
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

    def add_regions(self, regions, copy_from=None):
        """Extends the region list of a food balance sheet according to the
        defined input region list

        Parameters
        ----------
        fbs : xarray.Dataset
            Input food balance sheet Dataset
        new_regions : list, int, string
            list of region names to be added to the data
        copy_from : list, int, string
            If provided, this is the list of regions already on the food balance
            sheet to copy data from.
        labels : dict 
            Dictionary containing the new label for the regions matched to its
            corresponding label coordinate.
        
        Returns
        -------
        fbs : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with new regions added.
        """
        
        fbs = self._obj

        indexes = np.unique(regions, return_index=True)[1]
        regions = [regions[index] for index in sorted(indexes)]
        
        new_regions = xr.DataArray(data = np.ones(len(regions)),
                                coords = {"Region":regions})

        if copy_from is not None:
            fbs_pivot = fbs.sel(Region=copy_from)
            fbs_pivot["Region"] = regions
            new_fbs = fbs_pivot*new_regions
            
        else:
            new_regions *= np.nan
            new_fbs = fbs.isel(Region=0)*new_regions
            
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
        """Scales item quantities of an element and adds the difference to
        another element DataArray
        
        Parameters
        ----------
        fbs : xarray.Dataset
            Input DataSet with FAOSTAT like elements
        element_in : str
            Element DataArray to be scaled
        element_out : str
            Destination element DataArray to which the difference is added to
        scale : float, float array_like or xarray.Dataarray
            Scaling quantities for the element DataArray
        items : list of int or list of str, optional
            List of items to be scaled. If not provided, all items are scaled.
        add : boolean
            Wether to add or subtract the difference to element_out 
            
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

    def SSR(self, items=None, per_item=False, production="production",
            imports="imports", exports="exports"):
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
            return fbs[production] / (fbs[production] + fbs[imports] - fbs[exports])

        return fbs[production].sum(dim="Item") / (fbs[production]+fbs[imports]-fbs[exports]).sum(dim="Item")

    def IDR(self, items=None, per_item=False):
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

        Returns
        -------
        data : xarray.Datarray
            Import-dependency ratio or ratios for the list of items, one for
            each year of the input food Dataset "Year" coordinate.

        """

        fbs = self._obj

        if items is not None:
            if np.isscalar(items):
                items = [items]
            fbs = fbs.sel(Item=items)

        if per_item:
            return fbs["imports"] / (fbs["production"] + fbs["imports"] - fbs["exports"])

        return fbs["imports"].sum(dim="Item") / (fbs["production"]+fbs["imports"]-fbs["exports"]).sum(dim="Item")

    def plot_bars(self, show="Item", elements=None, inverted_elements=None,
                  ax=None, colors=None, labels=None, **kwargs):
        """Plot total quantities per element on a horizontal bar plot

        Produces a horizontal bar plot with a bar per element on the vertical
        axis plotted on a cumulative form. Each bar is the sum of quantities on
        each element, broken down by the selected coordinate "show". The
        starting x-axis position of each bar will depend on the cumulative value
        up to that element. The order of elements can be defined by the
        "element" parameter. A second set of "inverted_elements" can be given,
        and these will be plotted from right to left starting from the previous
        cumulative sum, minus the corresponding sum of the inverted elements. 

        Parameters
        ----------
        show : str, optional
            Name of the coordinate to dissagregate when filling the horizontal
            bar. The quantities are summed along the remaining coordinates.
        elements : str list, optional
            List of DataArray names in the Dataset to plot in ascending
            cumulative sum from left to right and top to bottom. If not
            provided, all DataArrays are plotted.
        inverted_elements : strr list, optional
            List of DataArray names in the Dataset to plot in descending
            cumulative sum from right to left, and top to bottom. If not
            provided, none of the DataArray is used.
        ax : matplotlib.pyplot.artist, optional
            Axes on which to draw the plot. If not provided, a new artist is
            created.
        colors : list of str, optional
            String list containing the colors for each of the elements in the
            "show" coordinate.
            If not defined, a color list is generated from the standard cycling.
        labels : str, list of str, optional
            String list containing the labels for the legend of the elements in
            the "show" coordinate. If not set, no labels are printed. If "show",
            the values of the "show" dimension are used.
        **kwargs : dict
            Style options to be passed on to the actual plot function, such as
            linewidth, alpha, etc.

        Returns
        -------
            ax : matplotlib axes instance
        """

        fbs = self._obj

        if ax is None:
            f, ax = plt.subplots(**kwargs)

        if elements is None:
            elements = list(fbs.keys())
            plot_elements = elements
        elif np.isscalar(elements):
            elements = [elements]

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
        print_labels = True
        if labels is None:
            # empty label placeholder and no-label flag
            labels = np.empty(len(fbs[show].values))
            print_labels = False

        elif np.all(labels == "show"):
            labels = fbs[show].values

        # Plot non inverted elements first
        cumul = 0
        for ie, element in enumerate(elements):
            ax.hlines(ie, 0, cumul, color="k", alpha=0.2, linestyle="dashed",
                    linewidth=0.5)
            if size_show == 1:
                ax.barh(ie, left = cumul, width=food_sum[element], 
                        color=colors[0])
                cumul +=food_sum[element]
            else:
                for ii, val in enumerate(food_sum[element]):
                    ax.barh(ie, left = cumul, width=val, color=colors[ii],
                            label=labels[ii])
                    cumul += val

        # Then the inverted elements
        if inverted_elements is not None:
            
            if np.isscalar(inverted_elements):
                inverted_elements = [inverted_elements]

            len_elements += len(inverted_elements)
            plot_elements = np.concatenate([elements, inverted_elements])

            cumul = 0
            for ie, element in enumerate(reversed(inverted_elements)):
                ax.hlines(len_elements-1 - ie, 0, cumul, color="k", alpha=0.2,
                        linestyle="dashed", linewidth=0.5)
                if size_show == 1:
                    ax.barh(len_elements-1 - ie, left = cumul,
                            width=food_sum[element], color=colors[0])
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
        ax.set_ylim(len_elements,-1)

        # Unique labels
        if print_labels:
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), fontsize=6)

        return ax

@xr.register_dataarray_accessor("fes")
class FoodElementSheet:
    def __init__(self, xarray_obj):
        self._validate(xarray_obj)
        self._obj = xarray_obj

    @staticmethod
    def _validate(obj):
        """Validate fbs xarray, checking it is a DataArray and has the minimum
        set of arrays
        """
        if not isinstance(obj, xr.DataArray):
            raise TypeError("Food Balance Sheet must be an xarray.DataSet")
        
    def add_regions(self, regions, copy_from=None):
        # use same function as fbs?
        pass

    def add_years(self, years, projection="empty"):
        # use same function as fbs?
        pass

    def add_items(self, items, copy_from=None):
        # use same function as fbs?
        pass

    def plot_years(self, show="Item", ax=None, colors=None, labels=None,
                   stack=True, **kwargs):
        """ Fill plot with quantities at each year value

        Produces a vertical fill plot with quantities for each year on the
        "Year" coordinate of the input dataset in the horizontal axis. If the
        "show" coordinate exists, then the vertical fill plot is a stack of the 
        sums of the other coordinates at that year for each item in the "show"
        coordinate.

        Parameters
        ----------
        food : xarray.Dataarray
            Input Dataarray containing a "Year" coordinate and optionally, a

        show : str, optional
            Name of the coordinate to dissagregate when filling the vertical
            plot. The quantities are summed along the remaining coordinates.
            If the coordinate is not provided or does not exist in the input,
            all coordinates are summed and a plot with a single fill curve is
            returned.
        ax : matplotlib.pyplot.artist, optional
            Axes on which to draw the plot. If not provided, a new artist is
            created.
        colors : list of str, optional
            String list containing the colors for each of the elements in the
            "show" coordinate.
            If not defined, a color list is generated from the standard cycling.
        labels : str, list of str, optional
            String list containing the labels for the legend of the elements in
            the "show" coordinate. If not set, no labels are printed. If "show",
            the values of the "show" dimension are used.
        **kwargs : dict
            Style options to be passed on to the actual plot function, such as
            linewidth, alpha, etc.

        Returns
        -------
            ax : matplotlib axes instance
        """

        fbs = self._obj

        # If no years are found in the dimensions, raise an exception
        sum_dims = list(fbs.dims)
        if "Year" not in sum_dims:
            raise TypeError("'Year' dimension not found in array data")

        # Define the cumsum and sum dims and check for one element dims
        sum_dims.remove("Year")
        if ax is None:
            f, ax = plt.subplots(1, **kwargs)

        if show in sum_dims:
            sum_dims.remove(show)
            size_cumsum = fbs.sizes[show]
            if stack:
                cumsum = fbs.cumsum(dim=show).transpose(show, ...)
            else:
                cumsum = fbs
        else:
            size_cumsum = 1
            cumsum = fbs

        # Collapse remaining dimensions
        cumsum = cumsum.sum(dim=sum_dims)
        years = fbs.Year.values

        # If colors are not defined, generate a list from the standard cycling
        if colors is None:
            colors = [f"C{ic}" for ic in range(size_cumsum)]

        # If labels are not defined, generate a list from the dimensions
        print_labels = True
        if labels is None:
            # empty label placeholder and no-label flag
            labels = np.empty(len(fbs[show].values))
            print_labels = False

        elif np.all(labels == "show"):
            labels = fbs[show].values

        # Plot
        if size_cumsum == 1:
            ax.fill_between(years, cumsum, color=colors[0], alpha=0.5)
            ax.plot(years, cumsum, color=colors[0], linewidth=0.5, label=labels)
        else:
            for id in reversed(range(size_cumsum)):
                ax.fill_between(years, cumsum[id], color=colors[id], alpha=0.5)
                ax.plot(years, cumsum[id], color=colors[id], linewidth=0.5,
                        label=labels[id])

        ax.set_xlim(years.min(), years.max())
        ax.set_ylim(bottom=0)

        if print_labels:
            ax.legend()

        return ax