"""Land module.
"""

import numpy as np
import xarray as xr
import os
import matplotlib.pyplot as plt
from itertools import product

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )

resolutions = [100, 200, 500, 1000, 2000]
datasets = ["CEH", "ALC"]
arrays = [f"{d}_{r}" for d, r in product(datasets, resolutions)]

@xr.register_dataarray_accessor("land")
class LandDataArray:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._validate(xarray_obj)

    @staticmethod
    def _validate(obj):
        """Validate land xarray, checking it is a DataSet and has the minimum set
        of coordinates
        """
        if not isinstance(obj, xr.DataArray):
            raise TypeError("Land array must be an xarray.Dataarray")
    
        if "x" not in obj.dims or "y" not in obj.dims:
            raise AttributeError("Land array must have 'x' and 'y' dimensions")

    def plot(self, ax=None, **kwargs):
        """Plot 2D map using imshow, without interpolation and without
        """

        map = self._obj

        if ax is None:
            f, ax = plt.subplots()

        # Get plot ranges
        xmin, xmax = map.x.values[[0, -1]]
        ymin, ymax = map.y.values[[0, -1]]

        ax.imshow(map, interpolation="none", origin="lower",
                  extent=[xmin, xmax, ymin, ymax])
        
    def area_by_type(self, values = None, dim = None):
        """Returns the total number of pixels where the value equals the input
        list of values.        
        """

        map = self._obj
        ones = xr.ones_like(map)

        if dim is None:
            dim = map.name

        if values is None:
            values = np.unique(map)

        # Prevent nan values from being counted
        nan_indices = np.isnan(values)
        values = values[~nan_indices]

        area = [ones.where(map==value).sum() for value in values]
        
        area_arr = xr.DataArray(area, dims=dim, coords={dim:values})

        return area_arr

    def area_overlap(self, map_right, values_left = None, values_right = None, dim_left=None, dim_right=None):

        map_left = self._obj

        # Check that both maps have the same dimensions and coordinates. if not,
        # this raises a ValueError
        xr.align(map_left, map_right, join='exact')

        if dim_left is None:
            dim_left = map_left.name

        if dim_right is None:
            dim_right = map_right.name

        if values_left is None:
            values_left = np.unique(map_left)

        if values_right is None:
            values_right = np.unique(map_right)

        # Prevent nan values from being counted
        nan_indices_left = np.isnan(values_left)
        nan_indices_right = np.isnan(values_right)

        values_left = values_left[~nan_indices_left]
        values_right = values_right[~nan_indices_right]

        ones = xr.ones_like(map_left)
        area = [[ones.where(map_left==vl).where(map_right==vr).sum().values for vr in values_right] for vl in values_left]

        area_arr = xr.DataArray(area, dims=[dim_left, dim_right], coords={dim_left:values_left, dim_right:values_right})

        return area_arr

@xr.register_dataset_accessor("land_ds")
class LandDataset:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._validate(xarray_obj)

    @staticmethod
    def _validate(obj):
        """Validate land_ds xarray, checking it is a DataArray and has the minimum set
        of arrays
        """
        if not isinstance(obj, xr.Dataset):
            raise TypeError("Land array must be an xarray.Dataset")
    
        if "x" not in obj.dims or "y" not in obj.dims:
            raise AttributeError("Land array must have 'x' and 'y' dimensions")

def __getattr__(name):
    if name not in arrays:
        raise AttributeError(f"{name!r} does not match a dataset and resoliution in {__name__!r}.")

    dataset, resolution = name.split('_')
    _data_file = f'{data_dir}{dataset}/{name}.nc'
    data = xr.open_dataset(_data_file)

    return data
