import numpy as np
import xarray as xr

from agrifoodpy.utils.nodes import load_dataset
import os


def test_load_dataset():

    items = ["Beef", "Apples", "Poultry"]
    shape = (3, 2, 2)
    data = np.reshape(np.arange(np.prod(shape)), shape)

    expected_ds = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                             coords={"Item": items, "X": [0, 1], "Y": [0, 1]})

    script_dir = os.path.dirname(__file__)
    test_data_path = os.path.join(script_dir, "data/test_dataset.nc")

    # Test loading a dataset from a file path
    ds = load_dataset(path=test_data_path)
    assert isinstance(ds, xr.Dataset)
    assert ds.equals(expected_ds)

    # Test loading a dataset and selecting a specific dataarray
    ds_dataarray = load_dataset(path=test_data_path, da="data")
    assert isinstance(ds_dataarray, xr.DataArray)
    assert ds_dataarray.equals(expected_ds["data"])

    # Test loading a dataset and selecting specific items
    sel = {"Item": ["Beef", "Apples"]}
    ds_selected = load_dataset(path=test_data_path, coords=sel)
    expected_selected_ds = expected_ds.sel(sel)
    assert ds_selected.equals(expected_selected_ds)

    # Test loading a dataset and applying a scale factor
    scaled_ds = load_dataset(path=test_data_path, scale=2.0)
    expected_scaled_data = expected_ds * 2.0
    assert scaled_ds.equals(expected_scaled_data)
