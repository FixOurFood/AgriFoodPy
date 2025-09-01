import numpy as np
import xarray as xr


def test_item_parser():

    from agrifoodpy.utils.dict_utils import item_parser
    items = ["Beef", "Apples", "Poultry"]

    item_origin = ["Animal", "Vegetal", "Animal"]

    data = np.random.rand(3, 2, 2)

    fbs = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                     coords={"Item": items, "X": [0, 1], "Y": [0, 1]})
    fbs = fbs.assign_coords({"Item_origin": ("Item", item_origin)})
    # Test case for item_parser with None input

    items = item_parser(fbs, None)
    assert items is None

    # Test case for item_parser with tuple input
    items = item_parser(fbs, ("Item_origin", ["Animal"]))
    assert np.array_equal(items, ["Beef", "Poultry"])

    # Tesct case for item_parser with scalar input
    items = item_parser(fbs, "Beef")
    assert np.array_equal(items, ["Beef"])


def test_get_dict():

    from agrifoodpy.utils.dict_utils import get_dict

    datablock = {
        "key1": {
            "key2": {
                "key3": "value"
            }
        },
        "key4": "another_value"
    }

    # Test case for get_dict with a single key
    value = get_dict(datablock, "key4")
    assert value == "another_value"

    # Test case for get_dict with a tuple of keys
    value = get_dict(datablock, ("key1", "key2", "key3"))
    assert value == "value"


def test_set_dict():

    from agrifoodpy.utils.dict_utils import set_dict

    datablock = {
        "key1": {
            "key2": {
                "key3": "value"
            }
        },
        "key4": "another_value"
    }

    # Test case for set_dict with a single key
    set_dict(datablock, "key4", "new_value")
    assert datablock["key4"] == "new_value"

    # Test case for set_dict with a tuple of keys
    set_dict(datablock, ("key1", "key2", "key3"), "new_nested_value")
    assert datablock["key1"]["key2"]["key3"] == "new_nested_value"

    # Test case for set_dict with create_missing=True
    set_dict(datablock, ("key5", "key6"), "missing_value", create_missing=True)
    assert datablock["key5"]["key6"] == "missing_value"

    # Test case for set_dict with create_missing=False
    try:
        set_dict(datablock, ("key7", "key8"), "should_fail",
                 create_missing=False)
    except KeyError:
        pass
