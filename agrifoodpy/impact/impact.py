"""Impact module.
"""

import numpy as np
import xarray as xr
from ..array_accessor import XarrayAccessorBase


def impact(
    items,
    regions,
    quantities,
    datasets=None,
    long_format=True
):
    """Impact style dataset constructor

    Parameters
    ----------
    items : (ny,) array_like
        The Item identifying ID or strings for which coordinates will be
        created.
    regions : (nr,) array_like, optional
        The region identifying ID or strings for which coordinates will be
        created.
    quantities : (ny, nr) ndarray
        Array containing the quantities for each combination of `Item` and
        `Region`.
    datasets : (nd,) array_like, optional
        Array with model name strings
    long_format : bool
        Boolean flag to interpret data in long or wide format

    Returns
    -------
    data : xarray.Dataset
        Impact dataset containing the impact for each `Item` and
        `Region` with one dataarray per element in `dataset`.
    """

    # if the input has a single element, proceed with long format
    if np.isscalar(quantities):
        long_format = True

    quantities = np.array(quantities)

    # Identify unique values in coordinates
    _items = np.unique(items)
    _regions = np.unique(regions)

    coords = {"Item": _items,
              "Region": _regions}

    # find positions in output array to organize data
    ii = [np.searchsorted(_items, items), np.searchsorted(_regions, regions)]
    size = (len(_items), len(_regions))

    # Create empty dataset
    data = xr.Dataset(coords=coords)

    if long_format:
        ndims = 2
    else:
        ndims = 3

    # make sure the long format has two dimensions
    # One along items and regions, one along datasets
    while len(quantities.shape) < ndims:
        quantities = np.expand_dims(quantities, axis=0)

    # If no dataset names are given, then create generic ones, one for each
    # dataset
    if datasets is None:
        datasets = [f"Impact {id}" for id in range(quantities.shape[0])]

    # Else, if a single string is given, transform to list. If doesn't match
    # the number of datasets created above, this will spit a list later.
    elif isinstance(datasets, str):
        datasets = [datasets]

    if long_format:
        # Create a datasets, one at a time
        for id, dataset in enumerate(datasets):
            values = np.zeros(size)*np.nan
            values[tuple(ii)] = quantities[id]
            data[dataset] = (coords, values)

    else:
        quantities = quantities[:, ii[0]]
        quantities = quantities[..., ii[1]]

        # Create a datasets, one at a time
        for id, dataset in enumerate(datasets):
            values = quantities[id]
            data[dataset] = (coords, values)

    return data


@xr.register_dataset_accessor("impact")
class Impact(XarrayAccessorBase):

    def __init__(self, xarray_obj):
        self._validate(xarray_obj)
        self._obj = xarray_obj

    @staticmethod
    def _validate(obj):
        """Check that the Impact object is an xarray.DataArray or xarray.
        Dataset"""
        if not isinstance(obj, xr.Dataset):
            raise TypeError("Food Balance Sheet must be an xarray.DataSet")

    def match(self, matching_matrix):
        """Matches an impact dataset to a new item base using a matching matrix

        Parameters
        ----------
        impact: xarray.DataSet
            xarray dataset including a list of items and impacts
        matching_matrix: pandas dataframe
            Defines how items are matched from the input to the output
            datasets, with the values of the matrix indicating the scaling of
            the impact quantities. Column names indicate the original item
            list, while row names indicate the new item list

        Returns
        -------
        dataset_out : xarray.Dataset
            FAOSTAT formatted Food Supply dataset with scaled quantities.

        """

        impact = self._obj

        out_items = matching_matrix["Item Code"]

        in_items = impact.Item.values

        # First column is the item code column
        in_items_mat = matching_matrix.columns[1:]

        assert np.equal(in_items, in_items_mat).all(), \
            "Input items do not match assignment matrix"

        # Again, we avoid first column
        mat = matching_matrix.iloc[:, 1:].fillna(0).to_numpy()

        dataset_out = xr.Dataset(
            coords=dict(
                Item=("Item", out_items),
            )
        )

        for var in list(impact.keys()):
            data_out = np.matmul(mat, impact[var].values)
            dataset_out = dataset_out.assign({var: ("Item", data_out)})

        return dataset_out
