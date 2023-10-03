import numpy as np
import xarray as xr
from agrifoodpy.food.food import FoodBalanceSheet
import pytest

def test_add_years():

    years = np.arange(2010, 2013)
    data = np.random.rand(3, 2, 2)
    new_years = [2013, 2014, 2015]
    expected_years = np.concatenate([years, new_years])

    ds = xr.Dataset({"data": (("Year", "X", "Y"), data)},
                      coords={"Year": years, "X": [0, 1], "Y": [0, 1]})
    
    fbs = FoodBalanceSheet(ds)

    # Test adding years with "empty" projection
    result_empty = fbs.add_years(new_years, projection="empty")

    assert np.array_equal(result_empty["Year"], expected_years)
    assert np.isnan(result_empty["data"].loc[dict(Year=new_years)].to_numpy()).all()

    # Test adding years with "constant" projection
    result_constant = fbs.add_years(new_years, projection="constant")
    last_year_data = ds["data"].isel(Year=-1).values

    assert np.array_equal(result_constant["Year"], expected_years)
    for year in new_years:
        assert np.array_equal(result_constant["data"].loc[dict(Year=year)].values, last_year_data)

    # Test adding years with specific projection
    projection = [0.5, 0.6, 0.7]  # Scaling factors
    result_projection = fbs.add_years(new_years, projection=projection)
    last_year_data = result_projection["data"].loc[dict(Year=years[-1])].values
    expected_data = [last_year_data * projection[i] for i in range(len(projection))]

    assert np.array_equal(result_projection["Year"], expected_years)
    assert np.allclose(result_projection["data"].loc[dict(Year=new_years)].values, expected_data)

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

    fbs = FoodBalanceSheet(ds)

    # Test adding new items
    result_add = fbs.add_items(new_items)

    assert np.array_equal(result_add["Item"].values, expected_items)
    assert np.isnan(result_add["data"].sel(Item=new_items).values).all()

    # Test adding new items copying from single existing one
    result_copy = fbs.add_items(new_items, copy_from="Beef")

    assert np.array_equal(result_copy["Item"], expected_items)
    for item_i in new_items:
        assert np.array_equal(result_copy["data"].sel(Item=item_i), ds.data.sel(Item="Beef"))

    # Test adding new items copying from existing array
    result_copy_multiple = fbs.add_items(new_items, copy_from=["Beef", "Apples", "Poultry"])

    assert np.array_equal(result_copy_multiple["Item"], expected_items)
    assert np.array_equal(result_copy_multiple["data"].sel(Item=new_items), ds.data.sel(Item=["Beef", "Apples", "Poultry"]))
  
def test_add_regions():

    regions = [1, 2, 3]
    region_name = ["UK", "US", "Chile"]
    new_regions = [4, 5, 6]

    data = np.random.rand(3, 2, 2)
    expected_regions = np.concatenate([regions, new_regions])

    ds = xr.Dataset({"data": (("Region", "X", "Y"), data)},
                    coords={"Region": regions, "X": [0, 1], "Y": [0, 1]})
    ds = ds.assign_coords({"Region_name":("Region", region_name)})

    fbs = FoodBalanceSheet(ds)

    # Test adding new regions
    result_add = fbs.add_regions(new_regions)

    assert np.array_equal(result_add["Region"], expected_regions)
    assert np.isnan(result_add["data"].sel(Region=new_regions).values).all()

    # Test adding new regions copying from single existing one
    result_copy = fbs.add_regions(new_regions, copy_from=1)

    assert np.array_equal(result_copy["Region"], expected_regions)
    for region_i in new_regions:
        assert np.array_equal(result_copy["data"].sel(Region=region_i), ds.data.sel(Region=1))

    # Test adding new regions copying from existing array
    result_copy_multiple = fbs.add_regions(new_regions, copy_from=[1, 2, 3])

    assert np.array_equal(result_copy_multiple["Region"], expected_regions)
    assert np.array_equal(result_copy_multiple["data"].sel(Region=new_regions), ds.data.sel(Region=[1, 2, 3]))

def test_SSR():

    items = ["Beef", "Apples"]
    years = [2020, 2021]

    ds = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]])
            ),

    coords=dict(Item=("Item", items), Year=("Year", years))
    )

    fbs = FoodBalanceSheet(ds)

    # Test basic result on all items

    result_basic = fbs.SSR()
    ex_result_basic = xr.DataArray([0.88, 0.810810], dims=("Year"),
                                coords={"Year": years})

    xr.testing.assert_allclose(result_basic, ex_result_basic)

    # Test for an item subset
    result_subset = fbs.SSR(items="Beef")
    ex_result_subset = xr.DataArray([0.909090, 0.823529], dims=("Year"),
                                    coords={"Year": years})

    xr.testing.assert_allclose(result_subset, ex_result_subset)

    # Test per item
    result_peritem = fbs.SSR(per_item=True)
    ex_result_peritem = xr.DataArray([[0.909090, 0.857142], [0.823529, 0.8]],
                                    dims=(["Year", "Item"]),
                                    coords={"Year": years, "Item": items})

    xr.testing.assert_allclose(result_peritem, ex_result_peritem)

def test_IDR():

    items = ["Beef", "Apples"]
    years = [2020, 2021]

    ds = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]])
            ),
      
    coords=dict(Item=("Item", items), Year=("Year", years))
    )

    fbs = FoodBalanceSheet(ds)

    # Test basic result on all items
    result_basic = fbs.IDR()
    ex_result_basic = xr.DataArray([0.24, 0.37837838], dims=("Year"),
                                   coords={"Year": years})
    
    xr.testing.assert_allclose(result_basic, ex_result_basic)

    # Test for an item subset
    result_subset = fbs.IDR(items="Beef")
    ex_result_subset = xr.DataArray([0.1818181, 0.352941], dims=("Year"),
                                    coords={"Year": years})
    
    xr.testing.assert_allclose(result_subset, ex_result_subset)

    # Test per item
    result_peritem = fbs.IDR(per_item=True)
    ex_result_peritem = xr.DataArray([[0.1818181, 0.285714], [0.352941, 0.4]],
                                     dims=(["Year", "Item"]),
                                     coords={"Year": years, "Item": items})
    
    xr.testing.assert_allclose(result_peritem, ex_result_peritem)

def test_FoodSupply():
    pass

def test_scale_add():

    items = ["Beef", "Apples"]
    years = [2020, 2021]

    scalar_scale = 1.5
    array_scale = np.arange(4).reshape((2,2))

    xarray_year_scale = xr.DataArray([1, 1.5], coords={'Year': years}, dims=['Year'])
    xarray_item_scale = xr.DataArray([1, 1.5], coords={'Item': items}, dims=['Item'])

    elin = "production"
    elout = "imports"

    im_data = np.array([[10, 20], [30, 40]])
    ex_data = np.array([[5, 10], [15, 20]])
    pr_data= np.array([[50, 60], [70, 80]])

    ds = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], im_data),
            exports=(["Year", "Item"], ex_data),
            production=(["Year", "Item"], pr_data)
            ),

    coords=dict(Item=("Item", items), Year=("Year", years))
    )

    fbs = FoodBalanceSheet(ds)

    fbs._obj

    # Test with float scale on all items
    result_scalar = fbs.scale_add(elin, elout, scalar_scale)
    assert np.array_equal(result_scalar[elin], ds[elin]*scalar_scale)
    assert np.array_equal(result_scalar[elout], ds[elout] +
                          (result_scalar[elin] - ds[elin]))

    # Test with float scale on all items with subtraction 
    result_scalar_sub = fbs.scale_add(elin, elout, scalar_scale, add=False)
    assert np.array_equal(result_scalar_sub[elin], ds[elin]*scalar_scale)
    assert np.array_equal(result_scalar_sub[elout], ds[elout] -
                          (result_scalar_sub[elin] - ds[elin]))

    # Test with float scale on some items
    result_scalar_item = fbs.scale_add(elin, elout, scalar_scale, items="Beef")
    assert np.array_equal(result_scalar_item[elin].sel(Item="Beef"),
                          ds[elin].sel(Item="Beef")*scalar_scale)
    
    assert np.array_equal(result_scalar_item[elout].sel(Item="Beef"),
                          ds[elout].sel(Item="Beef") + 
                          (result_scalar_item[elin].sel(Item="Beef")
                           - ds[elin].sel(Item="Beef")))
    
    assert np.array_equal(result_scalar_item[elin].sel(Item="Apples"),
                          ds[elin].sel(Item="Apples"))
    
    assert np.array_equal(result_scalar_item[elout].sel(Item="Apples"),
                          ds[elout].sel(Item="Apples"))

    # Test with float scale on some items with subtraction
    result_scalar_item_sub = fbs.scale_add(elin, elout, scalar_scale,
                                           items="Beef", add=False)
    
    assert np.array_equal(result_scalar_item_sub[elin].sel(Item="Beef"),
                          ds[elin].sel(Item="Beef")*scalar_scale)
    
    assert np.array_equal(result_scalar_item_sub[elout].sel(Item="Beef"),
                          ds[elout].sel(Item="Beef") -
                          (result_scalar_item_sub[elin].sel(Item="Beef")
                           - ds[elin].sel(Item="Beef")))
    
    assert np.array_equal(result_scalar_item_sub[elin].sel(Item="Apples"),
                          ds[elin].sel(Item="Apples"))
    
    assert np.array_equal(result_scalar_item_sub[elout].sel(Item="Apples"),
                          ds[elout].sel(Item="Apples"))

    # Test with array scale on all items
    result_array = fbs.scale_add(elin, elout, array_scale)
    assert np.array_equal(result_array[elin], ds[elin]*array_scale)
    assert np.array_equal(result_array[elout], ds[elout] + (result_array[elin]
                                                            - ds[elin]))

    # Test with DataArray scale on years only
    result_xarray_year = fbs.scale_add(elin, elout, xarray_year_scale)
    assert np.array_equal(result_xarray_year[elin], ds[elin]*xarray_year_scale)
    assert np.array_equal(result_xarray_year[elout], ds[elout]
                          + (result_xarray_year[elin] - ds[elin]))

    # Test with DataArray scale on items only
    result_xarray_item = fbs.scale_add(elin, elout, xarray_item_scale)
    assert np.array_equal(result_xarray_item[elin], ds[elin]*xarray_item_scale)
    assert np.array_equal(result_xarray_item[elout], ds[elout]
                          + (result_xarray_item[elin] - ds[elin]))

def test_scale_element():
    
    items = ["Beef", "Apples"]
    years = [2020, 2021]

    ds = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]])
            ),
        
        coords=dict(Item=("Item", items), Year=("Year", years))
        )
    
    fbs = FoodBalanceSheet(ds)

    # Scale single element by a single value
    result_single = fbs.scale_element("production", 0.5)
    xr.testing.assert_equal(result_single["production"], 0.5*ds["production"])
    xr.testing.assert_equal(result_single["imports"], ds["imports"])

    # Scale item subset
    result_subset = fbs.scale_element("production", 0.5, items="Beef")
    xr.testing.assert_equal(result_subset["production"],
                            [0.5, 1.0]*ds["production"])

    # Scale element array
    elements = ["production", "imports"]
    result_elements = fbs.scale_element(elements, 0.5)
    xr.testing.assert_equal(result_elements[elements], 0.5*ds[elements])
    xr.testing.assert_equal(result_elements["exports"], ds["exports"])

    # Scale by array of values
    scale_arr = [0.5, 2.0]
    result_arr = fbs.scale_element("production", scale_arr)
    xr.testing.assert_equal(result_arr["production"],
                            [0.5, 2.0]*ds["production"])


    # Scale by array of xarray along one named dimension
    scale_year = xr.DataArray([0.5, 2.0], dims="Year", coords={"Year":years})
    result_year = fbs.scale_element("production", scale_year)
    xr.testing.assert_equal(result_year["production"],
                            [[0.5], [2.0]]*ds["production"])
