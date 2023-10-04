import numpy as np
import xarray as xr
from agrifoodpy.array_accessor import XarrayAccessorBase

def test_add_years():

    years = np.arange(2010, 2013)
    data = np.random.rand(3, 2, 2)
    new_years = [2013, 2014, 2015]
    expected_years = np.concatenate([years, new_years])

    ds = xr.Dataset({"data": (("Year", "X", "Y"), data)},
                      coords={"Year": years, "X": [0, 1], "Y": [0, 1]})
    
    fbs = XarrayAccessorBase(ds)

    # Test adding years with "empty" projection
    result_empty = fbs.add_years(new_years, projection="empty")

    assert np.array_equal(result_empty["Year"], expected_years)
    assert np.isnan(result_empty["data"].loc[{"Year":new_years}].to_numpy()
                    ).all()

    # Test adding years with "constant" projection
    result_constant = fbs.add_years(new_years, projection="constant")
    last_year_data = ds["data"].isel(Year=-1).values

    assert np.array_equal(result_constant["Year"], expected_years)
    for year in new_years:
        assert np.array_equal(result_constant["data"].loc[{"Year":year}].values,
                              last_year_data)

    # Test adding years with specific projection
    proj = [0.5, 0.6, 0.7]  # Scaling factors
    result_projection = fbs.add_years(new_years, projection=proj)
    last_year_data = result_projection["data"].loc[dict(Year=years[-1])].values
    expected_data = [last_year_data * proj[i] for i in range(len(proj))]

    assert np.array_equal(result_projection["Year"], expected_years)
    assert np.allclose(result_projection["data"].loc[{"Year":new_years}].values,
                       expected_data)

    # Test for duplicate years
    new_years_duplicate = [2013, 2013, 2014, 2015]
    result_duplicate = fbs.add_years(new_years_duplicate)

    assert np.array_equal(result_duplicate["Year"], expected_years)

def test_add_items():

    items = ["Beef", "Apples", "Poultry"]
    item_origin = ["Animal", "Vegetal", "Animal"]
    new_items = ["Tomatoes", "Potatoes", "Eggs"]

    data = np.random.rand(3, 2, 2)
    expected_items = np.concatenate([items, new_items])

    ds = xr.Dataset({"data": (("Item", "X", "Y"), data)},
                    coords={"Item": items, "X": [0, 1], "Y": [0, 1]})
    ds = ds.assign_coords({"Item_origin":("Item", item_origin)})

    fbs = XarrayAccessorBase(ds)

    # Test adding new items
    result_add = fbs.add_items(new_items)

    assert np.array_equal(result_add["Item"].values, expected_items)
    assert np.isnan(result_add["data"].sel(Item=new_items).values).all()

    # Test adding new items copying from single existing one
    result_copy = fbs.add_items(new_items, copy_from="Beef")

    assert np.array_equal(result_copy["Item"], expected_items)
    for item_i in new_items:
        assert np.array_equal(result_copy["data"].sel(Item=item_i),
                              ds.data.sel(Item="Beef"))

    # Test adding new items copying from existing array
    result_copy_multiple = fbs.add_items(new_items, copy_from=["Beef",
                                                               "Apples",
                                                               "Poultry"])

    assert np.array_equal(result_copy_multiple["Item"], expected_items)
    assert np.array_equal(result_copy_multiple["data"].sel(Item=new_items),
                          ds.data.sel(Item=["Beef", "Apples", "Poultry"]))
  
def test_add_regions():

    regions = [1, 2, 3]
    region_name = ["UK", "US", "Chile"]
    new_regions = [4, 5, 6]

    data = np.random.rand(3, 2, 2)
    expected_regions = np.concatenate([regions, new_regions])

    ds = xr.Dataset({"data": (("Region", "X", "Y"), data)},
                    coords={"Region": regions, "X": [0, 1], "Y": [0, 1]})
    ds = ds.assign_coords({"Region_name":("Region", region_name)})

    fbs = XarrayAccessorBase(ds)

    # Test adding new regions
    result_add = fbs.add_regions(new_regions)

    assert np.array_equal(result_add["Region"], expected_regions)
    assert np.isnan(result_add["data"].sel(Region=new_regions).values).all()

    # Test adding new regions copying from single existing one
    result_copy = fbs.add_regions(new_regions, copy_from=1)

    assert np.array_equal(result_copy["Region"], expected_regions)
    for region_i in new_regions:
        assert np.array_equal(result_copy["data"].sel(Region=region_i),
                              ds.data.sel(Region=1))

    # Test adding new regions copying from existing array
    result_copy_multiple = fbs.add_regions(new_regions, copy_from=[1, 2, 3])

    assert np.array_equal(result_copy_multiple["Region"], expected_regions)
    assert np.array_equal(result_copy_multiple["data"].sel(Region=new_regions),
                          ds.data.sel(Region=[1, 2, 3]))