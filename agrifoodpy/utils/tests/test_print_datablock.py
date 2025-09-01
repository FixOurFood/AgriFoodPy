import numpy as np
import xarray as xr


def test_print_datablock():

    from agrifoodpy.utils.nodes import print_datablock

    items = ["Beef", "Apples", "Poultry"]

    data = np.random.rand(3, 2, 2)

    ds = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                    coords={"Item": items, "X": [0, 1], "Y": [0, 1]})

    datablock = {
        'test_dict': {
            'data': np.array([[1, 2], [3, 4]]),
            'years': [2020, 2021]
        },

        'test_xarray': ds,
        'test_string': "Hello, World!",
        'test_list': items,
        'test_array': data

    }

    # Test printing a dictionary element
    datablock = print_datablock(datablock, 'test_dict')

    # Test printing an xarray Dataset
    datablock = print_datablock(datablock, 'test_xarray')

    # Test printing a string
    datablock = print_datablock(datablock, 'test_string')

    # Test printing a list
    datablock = print_datablock(datablock, 'test_list')

    # Test printing an array
    datablock = print_datablock(datablock, 'test_array')

    # Test printing an attribute of the xarray Dataset
    datablock = print_datablock(datablock, 'test_xarray',
                                attr='data_vars')

    # Test calling a method on the xarray Dataset
    datablock = print_datablock(datablock, 'test_xarray',
                                method='mean', args=[('X', 'Y')])

    # Test calling a method with keyword arguments
    datablock = print_datablock(datablock, 'test_xarray',
                                method='sel', kwargs={'Item': 'Beef'})

    # Test error handling for non-existent attribute
    datablock = print_datablock(datablock, 'test_xarray',
                                attr='non_existent_attr')
