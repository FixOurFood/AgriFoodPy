import numpy as np
import xarray as xr

from agrifoodpy.pipeline.utils import item_parser

def test_item_parser_none():

    items = ["Beef", "Apples", "Poultry"]
    item_origin = ["Animal", "Vegetal", "Animal"]

    data = np.random.rand(3, 2, 2)

    fbs = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                    coords={"Item": items, "X": [0, 1], "Y": [0, 1]})
    fbs = fbs.assign_coords({"Item_origin":("Item", item_origin)})

    items = item_parser(fbs, None)
    assert items is None

def test_item_parser_tuple():
    items = ["Beef", "Apples", "Poultry"]
    item_origin = ["Animal", "Vegetal", "Animal"]

    data = np.random.rand(3, 2, 2)

    fbs = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                    coords={"Item": items, "X": [0, 1], "Y": [0, 1]})
    fbs = fbs.assign_coords({"Item_origin":("Item", item_origin)})

    items = item_parser(fbs, ("Item_origin", ["Animal"]))
    assert np.array_equal(items, ["Beef", "Poultry"])

def test_item_parser_scalar():
    items = ["Beef", "Apples", "Poultry"]
    item_origin = ["Animal", "Vegetal", "Animal"]

    data = np.random.rand(3, 2, 2)

    fbs = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                    coords={"Item": items, "X": [0, 1], "Y": [0, 1]})
    fbs = fbs.assign_coords({"Item_origin":("Item", item_origin)})

    items = item_parser(fbs, "Beef")

    assert np.array_equal(items, ["Beef"])

