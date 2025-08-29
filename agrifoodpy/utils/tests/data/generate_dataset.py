import xarray as xr
import numpy as np

items = ["Beef", "Apples", "Poultry"]

shape = (3, 2, 2)

data = np.reshape(np.arange(np.prod(shape)), shape)

ds = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                coords={"Item": items, "X": [0, 1], "Y": [0, 1]})

xr.Dataset.to_netcdf(ds, "test_dataset.nc")