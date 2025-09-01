import numpy as np
import xarray as xr


def test_add_items():

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
