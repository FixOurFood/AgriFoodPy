"""Impact module.
"""

import numpy as np
import xarray as xr
import os

data_dir = os.path.join(os.path.dirname(__file__), 'data/' )
available = ['PN18', 'PN18_FAOSTAT']

def impacts(items, impacts, quantities, regions=None):
    """Impact style dataset constructor

    Parameters
    ----------
    items : (ni,) array_like
        The item identifying ID or strings for which coordinates will be
        created.
    impacts : (nim,) array_like
        The impact name strings for which coordinates will be created.
    regions : (nr,) array_like, optional
        The region identifying ID or strings for which coordinates will be
        created.
    quantities : (nim, ni, [nr,]) ndarray
        Array containing the quantities for each combination of `Impact` and
        `Item`, and optionally each `Region` and element dataarray.

    Returns
    -------
    data : xarray.Dataset
        Impact dataset containing the quantities for each `Impact` and `Item`
        and, optionally, `Region`.
    """

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
    """Matches an impact dataset to a new item base using a matching matrix

    Parameters
    ----------
    impact: xarray.DataSet
        xarray dataset including a list of items and impacts
    matching_matrix: pandas dataframe
        Defines how items are matched from the input to the output datasets,
        with the values of the matrix indicating the scaling of the
        impact quantities. Column names indicate the original item list, while
        row names indicate the new item list

    Returns
    -------
    dataset_out : xarray.Dataset
        FAOSTAT formatted Food Supply dataset with scaled quantities.

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
