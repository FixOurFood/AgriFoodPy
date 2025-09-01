"""Land module.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import matplotlib.patches as mpatches


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

    def plot(self, ax=None, class_coord=None, colors=None, labels=None,
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
        class_coord : string
            Name of the coordinate to use as land classes. If not provided, the
            first non spatial coordinate is used.
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

        map = self._obj

        if ax is None:
            f, ax = plt.subplots()

        # Check the map type by checking for additional coordinates
        extra_coords = [dim for dim in map.dims if dim not in ["x", "y"]]
        if len(extra_coords) >= 1:
            if labels is None:
                labels = map[extra_coords[0]].values
            map = self.dominant_class(class_coord=class_coord)
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

    def area_by_type(
        self,
        values=None,
        dim=None
    ):
        """Area per map category in a LandDataArray

        Returns a DataArray with the total number of pixels for each category
        or category subset of the LandDataArray.

        Parameters
        ----------
        values : int, array
            List of category types to return the total area for. If not set,
            the function returns areas for all values found on the map,
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

        map = self._obj
        ones = xr.ones_like(map)

        if dim is None:
            dim = map.name

        if values is None:
            values = np.unique(map)
        else:
            values = np.array(values)

        # Prevent nan values from being counted
        nan_indices = np.isnan(values)
        values = values[~nan_indices]
        area = [ones.where(map == value).sum() for value in values]

        area_arr = xr.DataArray(area, dims=dim, coords={dim: values})

        return area_arr

    def area_overlap(
        self,
        map_right,
        values_left=None,
        values_right=None,
        dim_left=None,
        dim_right=None
    ):
        """Area overlap of selected categories between two maps

        Returns a DataArray with the total number of pixels for each
        combination of categories from the left and right map selected
        categories.

        Parameters
        ----------
        map_right : xarray.DataArray
            LandDataArray style DataArray to compare overlapping areas with
        values_left
            List of category types from the left map to return the total area
            overlaps for.
            If not set, all category types are used, except nan values.
        values_right : int, array
            List of category types from the right map to return the total area
            overlaps for.
            If not set, all category types are used, except nan values.
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
        map_left = self._obj

        # Check that both maps have the same dimensions and coordinates.
        # Otherwise, this raises a ValueError
        xr.align(map_left, map_right, join='exact')

        if dim_left is None:
            dim_left = map_left.name

        if dim_right is None:
            dim_right = map_right.name

        if values_left is None:
            values_left = np.unique(map_left)
        else:
            values_left = np.array(values_left)

        if values_right is None:
            values_right = np.unique(map_right)
        else:
            values_right = np.array(values_right)

        # Prevent nan values from being counted
        nan_indices_left = np.isnan(values_left)
        nan_indices_right = np.isnan(values_right)

        values_left = values_left[~nan_indices_left]
        values_right = values_right[~nan_indices_right]

        ones = xr.ones_like(map_left)
        area = [[ones.where(map_left == vl).where(map_right == vr).sum().values
                 for vr in values_right] for vl in values_left]

        area_arr = xr.DataArray(area,
                                dims=[dim_left, dim_right],
                                coords={dim_left: values_left,
                                        dim_right: values_right})

        return area_arr

    def category_match(
        self,
        map_right,
        values_left=None,
        values_right=None,
        join="left"
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
        map_left = self._obj

        # Check input values
        if values_left is None:
            values_left = np.unique(map_left)
        else:
            values_left = np.array(values_left)

        if values_right is None:
            values_right = np.unique(map_right)
        else:
            values_right = np.array(values_right)

        # Align maps to the left so they have the same dimensions
        map_left, map_right = xr.align(map_left, map_right, join=join)

        shape = map_left.shape

        left_match = np.in1d(map_left, values_left).reshape(shape)
        right_match = np.in1d(map_right, values_right).reshape(shape)

        category_match = map_left.where(left_match).where(right_match)

        return category_match

    def dominant_class(
        self,
        class_coord=None,
        return_index=False
    ):
        """Returns a land DataArray with the dominant land class for each
        pixel.

        Parameters
        ----------
        class_coord : string
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

        map = self._obj

        if class_coord is None:
            class_coord = [dim for dim in map.dims if dim not in ["x", "y"]][0]

        if return_index:
            len_class = len(map[class_coord].values)
            map = map.assign_coords({class_coord: np.arange(len_class)})

        map = map.idxmax(dim=class_coord, skipna=True)

        return map
