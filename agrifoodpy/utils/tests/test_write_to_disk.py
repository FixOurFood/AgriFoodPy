def test_write_csv(tmp_path):
    from agrifoodpy.utils.nodes import write_csv
    import pandas as pd
    import xarray as xr

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