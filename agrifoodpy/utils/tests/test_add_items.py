import numpy as np
import xarray as xr


def test_add_items():

    from agrifoodpy.utils.nodes import add_items

    items = ["Beef", "Apples", "Poultry"]
    item_origin = ["Animal", "Vegetal", "Animal"]
    new_items = ["Tomatoes", "Potatoes", "Eggs"]

    data = np.random.rand(3, 2, 2)
    expected_items = np.concatenate([items, new_items])

    ds = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                    coords={"Item": items, "X": [0, 1], "Y": [0, 1]})
    ds = ds.assign_coords({"Item_origin": ("Item", item_origin)})

    # Test basic functionality
    result_add = add_items(ds, new_items)

    assert np.array_equal(result_add["Item"].values, expected_items)
    for item in new_items:
        assert np.all(result_add["data"].sel(Item=item).values == 0)

    # Test copying from a single existing item
    result_copy = add_items(ds, new_items, copy_from="Beef")

    assert np.array_equal(result_copy["Item"], expected_items)
    for item_i in new_items:
        assert np.array_equal(result_copy["data"].sel(Item=item_i),
                              ds.data.sel(Item="Beef"))

    # Test copying from multiple existing items
    result_copy_multiple = add_items(ds, new_items, copy_from=["Beef",
                                                               "Apples",
                                                               "Poultry"])

    assert np.array_equal(result_copy_multiple["Item"], expected_items)
    assert np.array_equal(result_copy_multiple["data"].sel(Item=new_items),
                          ds.data.sel(Item=["Beef", "Apples", "Poultry"]))

    # Test providing values as dictionary
    new_items_dict = {
        "Item": new_items,
        "Item_origin": ["Vegetal", "Vegetal", "Animal"],
    }

    result_dict = add_items(ds, new_items_dict)

    assert np.array_equal(result_dict["Item"].values, expected_items)
    assert np.array_equal(result_dict["Item_origin"].values,
                          ["Animal", "Vegetal", "Animal",
                           "Vegetal", "Vegetal", "Animal"])
    for item in new_items:
        assert np.all(result_dict["data"].sel(Item=item).values == 0)
