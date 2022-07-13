import numpy as np
import xarray as xr
import os

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['PN18']

def impacts(items, impacts, quantities, regions=None):
    _impacts = np.unique(impacts)
    _items = np.unique(items)

    size = (len(_impacts), len(_items))

    ii = [np.searchsorted(_impacts, impacts), np.searchsorted(_items, items)]

    coords = {"Year" : _impacts,
              "Item" : _items}

    if regions is not None:
        _regions = np.unique(regions)
        ii.append(np.searchsorted(_regions, regions))
        size = size + (len(_regions),)
        coords["Region"] = _regions

    values = np.zeros(size)*np.nan

    values[tuple(ii)] = quantities

    data = xr.Dataset(data_vars = dict(value=(coords.keys(), values)), coords = coords)

    return data

def match(impact, matching_matrix):
    """
    returns an impact xarray dataset with items matched through a matching
    matrix.

    impact: xarray.DataSet
        xarray dataset including at least a list of items, and impacts

    matching_matrix: pandas dataframe
        Defines how items are matched from the impact dataset to the foodsupply
        DataSet, with the values of the matrix indicating the scaling of the
        impact quantities. Column names indicate the original item list.
        Row names indicate the new item list.
    """

    out_items = matching_matrix["Item Code"]

    in_items = impact.Item.values

    # First column is the item code column
    in_items_mat = matching_matrix.columns[1:]

    assert np.equal(in_items, in_items_mat).all() , "Input items do not match assignment matrix"

    # Again, we avoid first column
    mat = matching_matrix.iloc[:, 1:].fillna(0).to_numpy()

    dataset_out = xr.Dataset(
        coords = dict(
            Item=("Item", out_items),
        )
    )

    for var in list(impact.keys()):
        data_out = np.matmul(mat, impact[var].values)
        dataset_out = dataset_out.assign({var:("Item", data_out)})

    return dataset_out

def __getattr__(name):
    if name not in available:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}.")

    _data_file = f'{data_dir}{name}.nc'
    data = xr.open_dataset(_data_file)

    return data
