"""Land module.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import matplotlib.patches as mpatches
from warnings import warn

@xr.register_dataarray_accessor("land")
class LandDataArray:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._validate(xarray_obj)

    @staticmethod
    def _validate(obj):
        """Validate land xarray, checking it is a DataSet and has the minimum
        set of coordinates
        """
        if not isinstance(obj, xr.DataArray):
            raise TypeError("Land array must be an xarray.Dataarray")

        if "x" not in obj.dims or "y" not in obj.dims:
            raise AttributeError("Land array must have 'x' and 'y' dimensions")
        

    def plot(self, ax=None, category_dim=None, colors=None, labels=None,
             **kwargs):
        """Plot a LandDataArray

        Generates a plot of a LandDataArray using matplotlib imshow, without
        interpolation and setting the origin low to align north at the top.
        If a dominant classification map type is provided, the plot will be
        coloured accordingly. If a class percentage map is provided, the plot
        will be coloured according to the dominant class on each pixel.

        Parameters
        ----------
        ax : matplotlib.pyplot.Artist
            Axes on which to draw the plot
        category_dim : string
            Name of the dimension to use as land category. If not provided, the
            first non spatial dimension is used.
        colors : list of strings
            Dictionary of colors to use for each land class. If not provided,
            the default matplotlib colour map is used.
        labels : list of strings
            Dictionary of labels to use for each land class. If not provided
            and the map is a class percentage map, the coordinate values are
            used as labels.
        **kwargs : dict
            Style options to be passed to the imshow function.

        Returns
        -------
        ax : matplotlib axes instance
        """

        if "class_coord" in kwargs:
            warn("class_coord is deprecated as a keyword argument. "
                 "Please use category_dim instead.",
                 DeprecationWarning,
                 stacklevel=2)

            category_dim = kwargs.pop("class_coord")

        map = self._obj

        if ax is None:
            f, ax = plt.subplots()

        # Check the map type by checking for additional coordinates
        extra_coords = [dim for dim in map.dims if dim not in ["x", "y"]]
        if len(extra_coords) >= 1:
            if labels is None:
                labels = map[extra_coords[0]].values
            map = self.dominant_class(category_dim=category_dim)
        else:
            labels = np.unique(map.values)

        if colors is None:
            colors = [f"C{i}" for i in np.arange(len(labels))]

        # Create a colour map
        cmap = mcolors.ListedColormap(colors)
        bounds = np.linspace(-0.5, len(colors), len(colors) + 1)
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        # Get plot ranges
        dx_low = (map.x.values[1] - map.x.values[0])/2
        dx_high = (map.x.values[-1] - map.x.values[-2])/2
        dy_low = (map.y.values[1] - map.y.values[0])/2
        dy_high = (map.y.values[-1] - map.y.values[-2])/2

        xmin, xmax = map.x.values[[0, -1]]
        ymin, ymax = map.y.values[[0, -1]]

        print(map)

        ax.imshow(map, interpolation="none", origin="lower",
                  extent=[xmin-dx_low,
                          xmax+dx_high,
                          ymin-dy_low,
                          ymax+dy_high],
                  cmap=cmap, norm=norm)

        patches = [mpatches.Patch(color=colors[i],
                                  label=labels[i])
                   for i in np.arange(len(labels))]

        ax.legend(handles=patches, loc="best")

        return ax
    

    def area_by_type(self, values=None, dim=None):
        warn("The area_by_type method is deprecated and will be removed in a "
        "future version. Use area_by_category instead.",
        DeprecationWarning,
        stacklevel=2)

        return self.area_by_category(values=values, dim=dim)
    

    def area_by_category(
        self,
        categories=None,
        dim=None,
        **kwargs
    ):
        """Area per map category in a LandDataArray

        Returns a DataArray with the total number of pixels for each category
        or category subset of the LandDataArray.

        Parameters
        ----------
        values : int, array
            List of categories to return the total area for. If not set,
            the function returns areas for all categories found on the map,
            excluding nan values.
        dim : string
            Name to assign to the categories coordinate. If not set, the input
            DataArray name is used instead.

        Returns
        -------
        xarray.DataArray
            Array with the corresponding areas overlaps for each category
            combination.
        """

        if "values" in kwargs:
            warn("values is deprecated as a keyword argument. "
                 "Please use categories instead.",
                 DeprecationWarning,
                 stacklevel=2)

            categories = kwargs.pop("values")

        map = self._obj
        ones = xr.ones_like(map)

        if dim is None:
            dim = map.name

        if categories is None:
            categories = np.unique(map)
        else:
            categories = np.array(categories)

        # Prevent nan values from being counted
        nan_indices = np.isnan(categories)
        categories = categories[~nan_indices]
        area = [ones.where(map == value).sum() for value in categories]

        area_arr = xr.DataArray(area, dims=dim, coords={dim: categories})

        return area_arr


    def area_overlap(
        self,
        map_right,
        categories_left=None,
        categories_right=None,
        dim_left=None,
        dim_right=None,
        **kwargs
    ):
        """Area overlap of selected categories between two maps

        Returns a DataArray with the total number of pixels for each
        combination of categories from the left and right map selected
        categories.

        Parameters
        ----------
        map_right : xarray.DataArray
            LandDataArray style DataArray to compare overlapping areas with
        categories_left
            List of land categories from the left map to return the total area
            overlaps for.
            If not set, all categories are used, except nan values.
        categories_right : int, array
            List of land categories from the right map to return the total area
            overlaps for.
            If not set, all categories are used, except nan values.
        dim_left : string
            Names to assign to the category coordinates on the output
            DataArray.
            If not set, the input DataArray name is used instead.
        dim_right : string
            Names to assign to the category coordinates on the output
            DataArray.
            If not set, the input DataArray name is used instead.

        Returns
        -------
        area_arr : xarray.DataArray
            Array with the corresponding areas for each category type

        """

        if "values_left" in kwargs:
            warn("values_left is deprecated and will be removed in a future "
                 "version. Please use categories_left instead.",
                 DeprecationWarning,
                 stacklevel=2)
            
            categories_left = kwargs.pop("values_left")
                
        if "values_right" in kwargs:
            warn("values_right is deprecated and will be removed in a future "
                 "version. Please use categories_right instead.",
                 DeprecationWarning,
                 stacklevel=2)
            
            categories_right = kwargs.pop("values_right")
                


        map_left = self._obj

        # Check that both maps have the same dimensions and coordinates.
        # Otherwise, this raises a ValueError
        xr.align(map_left, map_right, join='exact')

        if dim_left is None:
            dim_left = map_left.name

        if dim_right is None:
            dim_right = map_right.name

        if categories_left is None:
            categories_left = np.unique(map_left)
        else:
            categories_left = np.array(categories_left)

        if categories_right is None:
            categories_right = np.unique(map_right)
        else:
            categories_right = np.array(categories_right)

        # Prevent nan values from being counted
        nan_indices_left = np.isnan(categories_left)
        nan_indices_right = np.isnan(categories_right)

        categories_left = categories_left[~nan_indices_left]
        categories_right = categories_right[~nan_indices_right]

        ones = xr.ones_like(map_left)
        area = [[ones.where(map_left == vl).where(map_right == vr).sum().values
                 for vr in categories_right] for vl in categories_left]

        area_arr = xr.DataArray(area,
                                dims=[dim_left, dim_right],
                                coords={dim_left: categories_left,
                                        dim_right: categories_right})

        return area_arr
    

    def category_match(
        self,
        map_right,
        categories_left=None,
        categories_right=None,
        join="left",
        **kwargs
    ):
        """Returns a land Dataarray with values where a selected overlap occurs
        between categories from two maps. This returns the values from the left
        map where coincidence occurs between the left and right map.

        Parameters
        ----------
        map_right : xarray.DataArray
            LandDataArray style DataArray to compare overlapping areas with
        values_left : int, array
            List of category types from the left map to match.
            If not set, all category types are used, except nan values.
        values_right : int, array
            List of category types from the right map to match.
            If not set, all category types are used, except nan values.

        Returns
        -------
        category_match : xarray.DataArray
            Land DataArray with values from the left map where overlap occurs.
            All other positions are assign a nan value.
        """

        if "values_left" in kwargs:
            warn("values_left is deprecated and will be removed in a future "
                 "version. Please use categories_left instead.",
                 DeprecationWarning,
                 stacklevel=2)
            
            categories_left = kwargs.pop("values_left")
                
        if "values_right" in kwargs:
            warn("values_right is deprecated and will be removed in a future "
                 "version. Please use categories_right instead.",
                 DeprecationWarning,
                 stacklevel=2)
            
            categories_right = kwargs.pop("values_right")

        map_left = self._obj

        # Check input values
        if categories_left is None:
            categories_left = np.unique(map_left)
        else:
            categories_left = np.array(categories_left)

        if categories_right is None:
            categories_right = np.unique(map_right)
        else:
            categories_right = np.array(categories_right)

        # Align maps to the left so they have the same dimensions
        map_left, map_right = xr.align(map_left, map_right, join=join)

        shape = map_left.shape

        left_match = np.isin(map_left, categories_left).reshape(shape)
        right_match = np.isin(map_right, categories_right).reshape(shape)

        category_match = map_left.where(left_match).where(right_match)

        return category_match


    def dominant_class(
        self,
        class_coord=None,
        return_index=False,
        **kwargs
    ):
        warn("The dominant_class method is deprecated and will be removed in" \
        " a future version. Please use dominant_category instead.",
        DeprecationWarning,
        stacklevel=2)

        return self.dominant_category(
            category_dim=class_coord,
            return_index=return_index,
            kwargs=kwargs)

    def dominant_category(
        self,
        category_dim=None,
        return_index=False,
        **kwargs
    ):
        """Returns a land DataArray with the dominant land class for each
        pixel.

        Parameters
        ----------
        category_dim : string
            Name of the land class coordinate. If not set, the first coordinate
            is used.
        return_index : bool
            If True, the index of the dominant class is returned instead of the
            class value.

        Returns
        -------
        xarray.DataArray
            Land DataArray with the dominant land class for each pixel.
        """

        if "class_coord" in kwargs:
            warn("class_coord is deprecated as a keyword argument. "
                 "Please use category_dim instead.",
                 DeprecationWarning,
                 stacklevel=2)
            
            category_dim = kwargs.pop("class_coord")

        map = self._obj

        if category_dim is None:
            category_dim = [dim for dim in map.dims if dim not in ["x", "y"]][0]

        if return_index:
            len_class = len(map[category_dim].values)
            map = map.assign_coords({category_dim: np.arange(len_class)})

        map = map.idxmax(dim=category_dim, skipna=True)

        return map


    def add_category(
        self,
        category,
        category_value=0,
        mask=None,
        category_dim=None,
    ):
        """Add a new land category to a LandDataArray

        Parameters
        ----------
        category : string, list of strings
            Name of the land class coordinate to add.
            Cannot contain values already present in the LandDataArray,
            or duplicated within the input list.
        category_value : int, xarray.DataArray
            Value of the new land class to add. If an array is provided, it
            must have the same shape as the spatial dimensions of the
            LandDataArray.
        mask : xarray.DataArray
            Boolean DataArray with the same spatial dimensions as the
            LandDataArray indicating where to add the new category.
            If not provided, the new category is added to all pixels.
        category_dim : string
            Name of the land class dimension. If not set, the first non spatial
            dimension is used.

        Returns
        -------
        xarray.DataArray
            Land DataArray with the new land category added.
        """

        map = self._obj

        # Use the first non spatial dimension if category dimension not provided
        if category_dim is None:
            category_dim = [d for d in map.dims if d not in ["x", "y", "Year"]][0]


        # Validate the mask input
        if mask is None:
            mask = xr.ones_like(map.isel({category_dim:0}), dtype=bool)
        else:
            if not isinstance(mask, xr.DataArray):
                raise TypeError("'mask' must be an xarray.DataArray")

            if set(mask.dims) != {"x", "y"}:
                raise ValueError("'mask' must have exactly the spatial " \
                "dimensions 'x' and 'y'")

            spatial_template = map.isel({category_dim: 0})
            try:
                xr.align(spatial_template, mask, join="exact")
            except ValueError as err:
                raise ValueError(
                    "'mask' must be aligned with the map spatial coordinates "
                    "'x' and 'y'"
                ) from err
            
        # Validate the category_value input
        if isinstance(category_value, (int, float)):
            category_value = xr.ones_like(
                map.isel({category_dim:0}))*category_value
            
        elif isinstance(category_value, xr.DataArray):
            if set(category_value.dims) != {"x", "y"}:
                raise ValueError("'category_value' must have exactly the " \
                "spatial dimensions 'x' and 'y'")
            
            spatial_template = map.isel({category_dim: 0})
            try:
                xr.align(spatial_template, category_value, join="exact")
            except ValueError as err:
                raise ValueError(
                    "'category_value' must be aligned with the map spatial " \
                    "coordinates 'x' and 'y'"
                ) from err
        else:
            raise TypeError("'category_value' must be either a scalar or an " \
            "xarray.DataArray with 'x' and 'y' dimensions")

        new_map = map.copy()

        if isinstance(category, str):
            category = [category]

        # Check that there are no duplicate category values in the input list
        if len(category) != len(set(category)):
            raise ValueError("Duplicate category values found in input list")

        # Check that the new category does not already exist in the map
        for cat in category:
            if cat in map[category_dim].values:
                raise ValueError(f"Category {cat} already exists in the"
                                 " LandDataArray")
            
            # Append new category values to the map
            new_class = xr.ones_like(map.isel({category_dim:0}))*category_value
            new_class = new_class.where(mask)
            new_class[category_dim] = cat
            new_map = xr.concat([new_map, new_class], dim=category_dim)

        return new_map
