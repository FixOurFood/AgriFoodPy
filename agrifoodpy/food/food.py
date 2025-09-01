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
from ..array_accessor import XarrayAccessorBase

import matplotlib.pyplot as plt


def FoodSupply(
    items,
    years,
    quantities,
    regions=None,
    elements=None,
    long_format=True
):
    """ Food Supply style dataset constructor

    Constructs a food balance sheet style xarray.Dataset or xarray.DataArray
    for a given list of items, years and regions, and an array data shaped
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
        is created for each element in `elements` with the quantities being
        each of the sub-arrays indexed by the first coordinate of the input
        array.

    Returns
    -------
    fbs : xarray.Dataset
        Food Supply dataset containing the food quantity for each `Item`,
        `Year` and `Region` with one dataarray per element in `elements`.
    """

    # if the input has a single element, proceed with long format
    if np.isscalar(quantities):
        long_format = True

    quantities = np.array(quantities)

    # Identify unique values in coordinates
    _items = np.unique(items)
    _years = np.unique(years)
    coords = {"Item": _items,
              "Year": _years}

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
    fbs = xr.Dataset(coords=coords)

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
class FoodBalanceSheet(XarrayAccessorBase):

    def scale_element(
        self,
        element,
        scale,
        items=None
    ):
        """Scales list of items from an element in a Food Balance Sheet like
        Dataset.

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
        sel = {"Item": items}

        out[element].loc[sel] = out[element].loc[sel] * scale

        return out

    def scale_add(
        self,
        element_in,
        element_out,
        scale,
        items=None,
        add=True,
        elasticity=None
    ):

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
        elasticity : float, float array_like optional
            Fractional percentage of the difference that is added to each
            element in element_out.

        Returns
        -------
        out : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with scaled quantities.

        """

        fbs = self._obj

        if np.isscalar(element_out):
            element_out = [element_out]

        if np.isscalar(add):
            add = [add] * len(element_out)

        # If no item elasticity is provided, divide elasticity equally
        if elasticity is None:
            elasticity = [1.0/len(element_out)] * len(element_out)
        elif np.isscalar(elasticity):
            elasticity = [elasticity] * len(element_out)

        out = self.scale_element(element_in, scale, items)
        dif = fbs[element_in].fillna(0) - out[element_in].fillna(0)

        for elmnt, add_el, elast in zip(element_out, add, elasticity):
            out[elmnt] = out[elmnt] + np.where(add_el, -1, 1)*dif*elast

        return out

    def SSR(
        self,
        items=None,
        per_item=False,
        domestic=None,
        production="production",
        imports="imports",
        exports="exports"
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
        domestic : string, optional
            Name of the DataArray containing the domestic use data
        production : string, optional
            Name of the DataArray containing the production data
        imports : string, optional
            Name of the DataArray containing the imports data
        exports : string, optional
            Name of the DataArray containing the exports data

        Returns
        -------
        data : xarray.Dataarray
            Self-sufficiency ratio or ratios for the list of items, one for
            each year of the input food Dataset "Year" coordinate.

        """

        fbs = self._obj

        if items is not None:
            if np.isscalar(items):
                items = [items]
            fbs = fbs.sel(Item=items)

        if domestic is not None:
            domestic_use = fbs[domestic]
        else:
            domestic_use = fbs[production] + fbs[imports] - fbs[exports]

        if per_item:
            return fbs[production] / domestic_use

        return fbs[production].sum(dim="Item") / domestic_use.sum(dim="Item")

    def IDR(
        self,
        items=None,
        per_item=False,
        imports="imports",
        domestic=None,
        production="production",
        exports="exports"
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
            Whether to return an IDR for each item separately. Default is
            false.
        domestic : string, optional
            Name of the DataArray containing the domestic use data
        imports : string, optional
            Name of the DataArray containing the imports data
        exports : string, optional
            Name of the DataArray containing the exports data
        production : string, optional
            Name of the DataArray containing the production data


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

        if domestic is not None:
            domestic_use = fbs[domestic]
        else:
            domestic_use = fbs[production] + fbs[imports] - fbs[exports]

        if per_item:
            return fbs["imports"] / domestic_use

        return fbs["imports"].sum(dim="Item") / domestic_use.sum(dim="Item")

    def plot_bars(
        self,
        show="Item",
        elements=None,
        inverted_elements=None,
        ax=None,
        colors=None,
        labels=None,
        **kwargs
    ):
        """Plot total quantities per element on a horizontal bar plot

        Produces a horizontal bar plot with a bar per element on the vertical
        axis plotted on a cumulative form. Each bar is the sum of quantities on
        each element, broken down by the selected coordinate "show". The
        starting x-axis position of each bar will depend on the cumulative
        value up to that element. The order of elements can be defined by the
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
            If not defined, a color list is generated from the standard
            cycling.
        labels : str, list of str, optional
            String list containing the labels for the legend of the elements in
            the "show" coordinate. If not set, no labels are printed.
            If "show", the values of the "show" dimension are used.
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
            elements = elements
        elif np.isscalar(elements):
            elements = [elements]

        len_elements = len(elements)

        # Define dimensions to sum over
        bar_dims = list(fbs.dims)
        if show in bar_dims:
            bar_dims.remove(show)
            size_show = fbs.sizes[show]
        elif show in fbs.coords:
            new_fbs = FoodBalanceSheet(fbs)
            new_fbs = FoodBalanceSheet(new_fbs.group_sum(coordinate=show))

            return new_fbs.plot_bars(
                show=show,
                elements=elements,
                inverted_elements=inverted_elements,
                ax=ax,
                colors=colors,
                labels=labels,
                **kwargs)
        else:
            raise ValueError(f"The coordinate {show} is not a valid "
                             "dimension or coordinate of the Dataset.")

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
            labels = np.empty(len(fbs[show].values), dtype=str)
            print_labels = False

        elif np.all(labels == "show"):
            labels = [str(val) for val in fbs[show].values]

        # Plot non inverted elements first
        cumul = 0
        for ie, element in enumerate(elements):
            ax.hlines(ie, 0, cumul, color="k", alpha=0.2, linestyle="dashed",
                      linewidth=0.5)
            if size_show == 1:
                ax.barh(ie, left=cumul, width=food_sum[element],
                        color=colors[0])
                cumul += food_sum[element]
            else:
                for ii, val in enumerate(food_sum[element]):
                    ax.barh(ie, left=cumul, width=val, color=colors[ii],
                            label=labels[ii])
                    cumul += val

        # Then the inverted elements
        if inverted_elements is not None:

            if np.isscalar(inverted_elements):
                inverted_elements = [inverted_elements]

            len_elements += len(inverted_elements)
            elements = np.concatenate([elements, inverted_elements])

            cumul = 0
            for ie, element in enumerate(reversed(inverted_elements)):
                ax.hlines(len_elements-1 - ie, 0, cumul, color="k", alpha=0.2,
                          linestyle="dashed", linewidth=0.5)
                if size_show == 1:
                    ax.barh(len_elements-1 - ie, left=cumul,
                            width=food_sum[element], color=colors[0])
                    cumul += food_sum[element]
                else:
                    for ii, val in enumerate(food_sum[element]):
                        ax.barh(len_elements-1 - ie, left=cumul, width=val,
                                color=colors[ii], label=labels[ii])
                        cumul += val

        # Plot decorations
        ax.set_yticks(np.arange(len_elements), labels=elements)
        ax.tick_params(axis="x", direction="in", pad=-12)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_ylim(len_elements, -1)

        # Unique labels
        if print_labels:
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), fontsize=6)

        return ax


@xr.register_dataarray_accessor("fbs")
class FoodElementSheet(XarrayAccessorBase):
    def plot_years(
            self,
            show=None,
            stack=True,
            ax=None,
            colors=None,
            labels=None,
            **kwargs
    ):
        """ Fill plot with quantities at each year value

        Produces a vertical fill plot with quantities for each year on the
        "Year" coordinate of the input dataset in the horizontal axis. If the
        "show" coordinate exists, then the vertical fill plot is a stack of the
        sums of the other coordinates at that year for each item in the "show"
        coordinate.

        Parameters
        ----------
        food : xarray.Dataarray
            Input Dataarray containing a "Year" coordinate and optionally,
            additional coordinates to dissagregate.
        show : str, optional
            Name of the coordinate to dissagregate when filling the vertical
            plot. The quantities are summed along the remaining coordinates.
            If the coordinate is not provided or does not exist in the input,
            all coordinates are summed and a plot with a single fill curve is
            returned.
        stack : boolean, optional
            Whether to stack fill plots or not. If 'True', the fill curves are
            stacked on top of each other and the upper fill curve represents
            the sum of all elements for a given year.
            If 'false', each element along the 'show' dimension is plotted
            starting from the origin.
        ax : matplotlib.pyplot.artist, optional
            Axes on which to draw the plot. If not provided, a new artist is
            created.
        colors : list of str, optional
            String list containing the colors for each of the elements in the
            "show" coordinate.
            If not defined, a color list is generated from the standard
            cycling.
        labels : str, list of str, optional
            String list containing the labels for the legend of the elements in
            the "show" coordinate. If not set, no labels are printed.
            If "show", the values of the "show" dimension are used.
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

        # Define new ax if not provided
        if ax is None:
            f, ax = plt.subplots(1, **kwargs)

        # Define the cumsum and sum dims and check for one element dims
        sum_dims.remove("Year")
        if show in sum_dims:
            sum_dims.remove(show)
            size_cumsum = fbs.sizes[show]
            if stack:
                cumsum = fbs.cumsum(dim=show).transpose(show, ...)
            else:
                cumsum = fbs
        elif show in fbs.coords:
            new_fbs = FoodElementSheet(fbs)
            new_fbs = FoodElementSheet(new_fbs.group_sum(coordinate=show))

            return new_fbs.plot_years(show=show, stack=stack, ax=ax,
                                      colors=colors, labels=labels, **kwargs)
        elif show is None:
            size_cumsum = 1
            cumsum = fbs
        else:
            raise ValueError(f"The coordinate {show} is not a valid "
                             "dimension or coordinate of the Dataarray.")

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
            if show is not None:
                labels = np.empty(len(fbs[show].values))
            else:
                labels = np.empty(len(fbs["Year"].values))
            print_labels = False

        elif np.all(labels == "show") and show is not None:
            labels = fbs[show].values

        # Plot
        if size_cumsum == 1:
            ax.fill_between(years, cumsum, color=colors[0], alpha=0.5)
            ax.plot(years, cumsum, color=colors[0], linewidth=0.5,
                    label=labels)
        else:
            ax.fill_between(years, cumsum.isel({show: 0}), color=colors[0],
                            alpha=0.5)
            ax.plot(years, cumsum.isel({show: 0}), color=colors[0],
                    linewidth=0.5, label=labels[0])
            for id in range(1, size_cumsum):
                ax.fill_between(years, cumsum.isel({show: id}),
                                cumsum.isel({show: id-1}), color=colors[id],
                                alpha=0.5)
                ax.plot(years, cumsum.isel({show: id}), color=colors[id],
                        linewidth=0.5, label=labels[id])

        ax.set_xlim(years.min(), years.max())
        ax.set_ylim(bottom=0)
        ax.set_xlabel("Year")

        if print_labels:
            ax.legend()

        return ax
