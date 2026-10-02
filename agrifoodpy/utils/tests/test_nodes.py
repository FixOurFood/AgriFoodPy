import numpy as np
import xarray as xr
import pandas as pd

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


def test_add_years():

    from agrifoodpy.utils.nodes import add_years

    items = ["Beef", "Apples", "Poultry"]
    years = [2010, 2011, 2012]

    shape = (3, 3)
    data = np.reshape(np.arange(np.prod(shape)), shape)

    ds = xr.Dataset({"data": (("Item", "Year"), data)},
                    coords={"Item": items, "Year": years})

    # Test basic functionality
    new_years = [2013, 2014]
    result_add = add_years(ds, new_years)
    expected_years = years + new_years
    assert np.array_equal(result_add["Year"].values, expected_years)
    for year in new_years:
        assert np.all(np.isnan(result_add["data"].sel(Year=year).values))

    # Test projection mode 'constant'
    result_constant = add_years(ds, new_years, projection='constant')
    assert np.array_equal(result_constant["Year"].values, expected_years)
    for year in new_years:
        assert np.array_equal(result_constant["data"].sel(Year=year).values,
                              ds.data.isel(Year=-1).values)

    # Test projection mode with float array
    scaling_factors = np.array([1.0, 2.0])
    result_scaled = add_years(ds, new_years, projection=scaling_factors)
    assert np.array_equal(result_scaled["Year"].values, expected_years)
    for i, year in enumerate(new_years):
        expected_values = ds.data.isel(Year=-1).values * scaling_factors[i]
        assert np.array_equal(result_scaled["data"].sel(Year=year).values,
                              expected_values)


def test_copy_datablock():

    from agrifoodpy.pipeline import Pipeline
    from agrifoodpy.utils.nodes import copy_datablock

    datablock = {
        'test_dataset': {
            'fbs': {
                'data': np.array([[1, 2], [3, 4]]),
                'years': [2020, 2021]
            }
        }
    }

    # Test copying the datablock
    pipeline = Pipeline(datablock=datablock)
    pipeline.add_node(
        copy_datablock,
        params={
            'key': 'test_dataset',
            'out_key': 'copied_dataset'
        },
    )

    # Execute the pipeline
    pipeline.run()

    # Check if the copied dataset exists in the datablock
    assert 'copied_dataset' in pipeline.datablock
    assert np.array_equal(
        pipeline.datablock['copied_dataset']['fbs']['data'],
        datablock['test_dataset']['fbs']['data']
    )


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


def test_write_to_datablock():
    from agrifoodpy.utils.nodes import write_to_datablock

    datablock_basic = {}

    # Basic write to the datablock
    write_to_datablock(datablock_basic, "test_key", "test_value")
    assert datablock_basic["test_key"] == "test_value"

    # Write to the datablock with a tuple value
    datablock_tuple = {}
    write_to_datablock(
        datablock=datablock_tuple,
        key=("test_key_1", "test_key_2"),
        value="test_tuple_value"
        )
    assert datablock_tuple["test_key_1"]["test_key_2"] == "test_tuple_value"

    # Overwrite existing key
    datablock_overwrite = {"test_key": "old_value"}
    write_to_datablock(datablock_overwrite, "test_key", "new_value")
    assert datablock_overwrite["test_key"] == "new_value"

    # Attempt to write without overwriting an existing key
    datablock_no_overwrite = {"test_key": "existing_value"}
    try:
        write_to_datablock(
            datablock=datablock_no_overwrite,
            key="test_key",
            value="new_value",
            overwrite=False)

    except KeyError as e:
        assert str(e) == "'Key already exists in datablock and overwrite is set to False.'"




def test_load_dataset():
    from agrifoodpy.utils.nodes import load_dataset
    import os

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


def test_write_csv(tmp_path):
    from agrifoodpy.utils.nodes import write_csv

    # Test unsupported type
    datablock_unsupported = {"data": set([1, 2, 3])}
    try:
        write_csv(datablock_unsupported, key="data", path=tmp_path / "test.csv")
    except TypeError as e:
        assert str(e) == "write_csv does not support objects of type set. Expected xr.Dataset, xr.DataArray, pd.DataFrame, or pd.Series."

    # Test Pandas DataFrame
    df = pd.DataFrame(
        {
            "Item": ["Beef", "Beef", "Apples", "Apples"],
            "Year": [2020, 2021, 2020, 2021],
            "production": [15, 20, 6, 7]
        }
    )

    datablock_df = {"data": df}
    path = tmp_path / "test_df_output.csv"

    write_csv(datablock_df, key="data", path=path)

    df = pd.read_csv(path, index_col=0, header=0)
    assert df.shape == (4, 3)
    assert list(df.columns) == ["Item", "Year", "production"]
    assert df.iloc[0]["Item"] == "Beef"
    assert df.iloc[0]["Year"] == 2020
    assert df.iloc[0]["production"] == 15

    assert df.iloc[1]["Item"] == "Beef"
    assert df.iloc[1]["Year"] == 2021
    assert df.iloc[1]["production"] == 20

    # Test Pandas Series
    series = pd.Series(
        [15, 6, 30],
        index=["Beef", "Apples", "Poultry"],
        name="production",
        )
    
    datablock_series = {"data": series}
    path = tmp_path / "test_series_output.csv"

    write_csv(datablock_series, key="data", path=path)

    df = pd.read_csv(path, index_col=0, header=0)
    assert df.shape == (3, 1)
    assert list(df.columns) == ["production"]
    assert df.loc["Beef", "production"] == 15
    assert df.loc["Apples", "production"] == 6
    assert df.loc["Poultry", "production"] == 30

    # Test xarray Dataset
    ds = xr.Dataset(
        {
            "production": (("Item", "Year"), [[15, 20], [6, 7]]),
            "imports": (("Item", "Year"), [[4, 5], [1, 2]]),
        },
        coords={
            "Item": ["Beef", "Apples"],
            "Year": ["2020", "2021"],
        },
    )

    datablock_ds = {"data": ds}
    path = tmp_path / "test_ds_output.csv"

    write_csv(datablock_ds, key="data", path=path)

    df = pd.read_csv(path, header=0)

    assert df.shape == (4, 4)
    assert list(df.columns) == ["Item", "Year", "production", "imports"]
    assert df.iloc[0]["Item"] == "Beef"
    assert df.iloc[0]["Year"] == 2020
    assert df.iloc[0]["production"] == 15
    assert df.iloc[0]["imports"] == 4

    # Test xarray DataArray
    da = xr.DataArray(
        [[15, 20], [6, 7]],
        coords={
            "Item": ["Beef", "Apples"],
            "Year": ["2020", "2021"],
        },
        dims=["Item", "Year"],
        name="production",
    )

    datablock_da = {"data": da}
    path = tmp_path / "test_da_output.csv"

    write_csv(datablock_da, key="data", path=path)

    df = pd.read_csv(path, header=0)

    assert df.shape == (4, 3)
    assert list(df.columns) == ["Item", "Year", "production"]
    assert df.iloc[0]["Item"] == "Beef"
    assert df.iloc[0]["Year"] == 2020
    assert df.iloc[0]["production"] == 15

    # Test unnamed xarray DataArray
    datablock_key = "data"

    da_unnamed = xr.DataArray(
        [[15, 20], [6, 7]],
        coords={
            "Item": ["Beef", "Apples"],
            "Year": ["2020", "2021"],
        },
        dims=["Item", "Year"],
    )

    datablock_da_unnamed = {datablock_key: da_unnamed}
    path = tmp_path / "test_da_unnamed_output.csv"

    write_csv(datablock_da_unnamed, key=datablock_key, path=path)

    df = pd.read_csv(path, header=0)

    assert df.shape == (4, 3)
    assert list(df.columns) == ["Item", "Year", datablock_key]
