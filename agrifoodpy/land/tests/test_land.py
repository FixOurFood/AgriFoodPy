import numpy as np
import xarray as xr
from agrifoodpy.land.land import LandDataArray
import pytest
import matplotlib.pyplot as plt

def test_area_by_category():
    
    data = np.tile((np.arange(3, dtype=float)), (4,1))

    da = xr.DataArray(data=data, name="land",
                    coords={"x": [0, 1, 2, 3], "y": [0, 1, 2]})

    land = LandDataArray(da)
    # Test area by category without explicit categories
    expected_result_no_categories = np.array([4,4,4])
    result_no_categories = land.area_by_category()
    
    assert(np.array_equal(expected_result_no_categories, result_no_categories))
    assert(list(result_no_categories.coords) == ["land"])

    # Test area by category with explicit categories
    expected_result_categories = np.array([4,4])
    result_categories = land.area_by_category(categories=[1,2])
    
    assert(np.array_equal(expected_result_categories, result_categories))
    assert(list(result_categories.coords) == ["land"])

    # Test area by category with explicit dimension name
    dim_name = "area"
    expected_result_dims = np.array([4,4,4])
    result_dims = land.area_by_category(dim=dim_name)
    
    assert(np.array_equal(expected_result_dims, result_dims))
    assert(list(result_dims.coords) == [dim_name])

    # Test area by category with nan categories
    da_nan = da.copy(deep=True)
    da_nan[-1, -1] = np.nan
    da_nan.name = "land_nan"
    land_nan = LandDataArray(da_nan)

    expected_result_nan = np.array([4,4,3])
    result_nan = land_nan.area_by_category()

    assert(np.array_equal(expected_result_nan, result_nan))
    assert(list(result_nan.coords) == ["land_nan"])

def test_area_overlap():

    data_left = np.tile((np.arange(3, dtype=float)), (4,1))
    data_right = np.repeat((np.arange(4, dtype=float)), 3).reshape((4,3))

    name_left, name_right = "land_left", "land_right"

    da_left = xr.DataArray(data=data_left, name=name_left,
                    coords={"x": [0, 1, 2, 3], "y": [0, 1, 2]})
    
    da_right = xr.DataArray(data=data_right, name=name_right,
                    coords={"x": [0, 1, 2, 3], "y": [0, 1, 2]})

    land_left = LandDataArray(da_left)
    land_right = LandDataArray(da_right)

    # Test area overlap without explicit categories

    expected_results_no_cats = np.ones((3,4))
    result_no_cats = land_left.area_overlap(da_right)

    assert(np.array_equal(expected_results_no_cats, result_no_cats))
    assert(list(result_no_cats.coords) == [name_left, name_right])

    # Test area overlap with explicit categories
    input_cat_left = [1,2]
    input_cat_right = [2,3]

    expected_results_categories = np.ones((2,2))
    result_cats = land_left.area_overlap(da_right,
                                           categories_left=input_cat_left,
                                           categories_right=input_cat_right)
    
    assert(np.array_equal(expected_results_no_cats, result_no_cats))
    assert(np.array_equal(result_no_cats.coords, [name_left, name_right]))
    assert(np.array_equal(result_cats[name_left].values, input_cat_left))
    assert(np.array_equal(result_cats[name_right].values, input_cat_right))

    # Test area overlap with explicit dimension names

    dim_left, dim_right = "category_left", "category_right"

    expected_results_dimensions = np.ones((3,4))
    result_dimensions = land_left.area_overlap(da_right,
                                              dim_left=dim_left,
                                              dim_right=dim_right)

    assert(np.array_equal(expected_results_dimensions, result_dimensions))
    assert(np.array_equal(result_dimensions.coords, [dim_left, dim_right]))

    # Test area overlap with nan values

    da_left_nan = da_left.copy(deep=True)
    da_left_nan[-1,-1] = np.nan
    da_left_nan.name = "land_left_nan"
    land_left_nan = LandDataArray(da_left_nan)

    da_right_nan = da_right.copy(deep=True)
    da_right_nan[0,0] = np.nan
    da_right_nan.name = "land_right_nan"

    expected_results_nan = np.ones((3,4))
    expected_results_nan[-1,-1] = 0
    expected_results_nan[0,0] = 0

    result_nan = land_left_nan.area_overlap(da_right_nan)

    assert(np.array_equal(expected_results_nan, result_nan))
    
def test_category_match():

    data_left = np.tile((np.arange(3, dtype=float)), (4,1))
    data_right = np.repeat((np.arange(4, dtype=float)), 3).reshape((4,3))

    name_left, name_right = "land_left", "land_right"

    da_left = xr.DataArray(data=data_left, name=name_left,
                    coords={"x": [0, 1, 2, 3], "y": [0, 1, 2]})
    
    da_right = xr.DataArray(data=data_right, name=name_right,
                    coords={"x": [0, 1, 2, 3], "y": [0, 1, 2]})

    land_left = LandDataArray(da_left)
    land_right = LandDataArray(da_right)

    # Basic example without set values
    result_basic = land_left.category_match(da_right)
    assert result_basic.equals(da_left)
    assert result_basic.name == name_left

    # Example with values on left map
    result_values_left = land_left.category_match(da_right, categories_left=1)
    assert result_values_left.where(result_values_left==1).equals(
        da_left.where(da_left==1))
    assert np.all(result_values_left.where(result_values_left!=1).isnull())

    # Example with values on right map
    result_values_left = land_left.category_match(da_right, categories_right=1)
    
    # Example with multiple values on both maps
    result_multivar = land_left.category_match(da_right,
                                               categories_left=[0,1],
                                               categories_right=[1,2])

    non_nan_values = result_multivar.where(~np.isnan(result_multivar),
                                           drop=True)
    truth = np.array([[0., 1.], [0., 1.]])
    assert np.array_equal(non_nan_values, truth)
    assert np.array_equal(non_nan_values.x.values, [1, 2])
    assert np.array_equal(non_nan_values.y.values, [0, 1])
    assert result_multivar.name == name_left

    # Example with non-matching values
    result_non_matching = land_left.category_match(da_right, categories_left=4)
    assert np.all(result_non_matching.isnull())

def test_plot():
    
    data = np.random.rand(4, 5)
    da = xr.DataArray(data, dims=['x', 'y'])
    land = LandDataArray(da)
    
    # Test default plot
    ax = land.plot()
    assert isinstance(ax, plt.Axes)

def test_dominant_class():
    classes = ["a", "b", "c"]
    coords = {"x": [0, 1, 2, 3], "y": [0, 1, 2], "class": classes}
    coords_index = {"x": [0, 1, 2, 3], "y": [0, 1, 2]}
    
    data = np.random.rand(len(coords["x"]),
                          len(coords["y"]),
                          len(coords["class"]))
    
    da = xr.DataArray(data, coords=coords)
    land = LandDataArray(da)

    # Test dominant class without coord name
    result_no_coord = land.dominant_category()
    assert result_no_coord.equals(da.idxmax(dim="class"))

    # Test dominant class with coord name
    result_coord = land.dominant_category(category_dim="class")
    assert result_coord.equals(da.idxmax(dim="class"))

    # Test dominant class with non-matching coord name
    with pytest.raises(KeyError):
        result_non_matching = land.dominant_category(category_dim="non_matching")

    # Test with return index set to True
    result_return_index = land.dominant_category(return_index=True)
    result_return_index_truth = xr.DataArray(np.argmax(data, axis=2),
                                             coords=coords_index)

    assert result_return_index.equals(result_return_index_truth)

def test_add_category_basic():
    categories = ["a", "b"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }
    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    da = xr.DataArray(data, coords=coords)
    land = LandDataArray(da)

    result = land.add_category("c")
    assert "c" in result["categories"].values
    assert np.all(result.sel(categories="c") == 0)

def test_add_category_with_value():
    categories = ["a", "b"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }
    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    da = xr.DataArray(data, coords=coords)
    land = LandDataArray(da)
    category_value = 1

    result = land.add_category("c", category_value=category_value)
    assert "c" in result["categories"].values
    assert np.all(result.sel(categories="c") == category_value)

def test_add_category_with_array_value():
    categories = ["a", "b"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }
    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    da = xr.DataArray(data, coords=coords)
    land = LandDataArray(da)

    value_array_data = np.random.rand(len(coords["x"]), len(coords["y"]))

    value_array = xr.DataArray(
        value_array_data,
        dims=["x", "y"],
        coords={"x": coords["x"], "y": coords["y"]},
    )

    result = land.add_category("c", category_value=value_array)
    assert "c" in result["categories"].values
    xr.testing.assert_allclose(
        result.sel(categories="c").drop_vars("categories"),
        value_array)

def test_add_category_with_mask():
    categories = ["a", "b"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }
    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    da = xr.DataArray(data, coords=coords)
    land = LandDataArray(da)

    mask_array = xr.DataArray(
        np.array([[True, False], [False, True], [True, True]]),
        dims=["x", "y"],
        coords={"x": coords["x"], "y": coords["y"]},
    )

    ex_result = xr.ones_like(mask_array).where(mask_array)

    result = land.add_category("c", category_value=1, mask=mask_array)
    assert "c" in result["categories"].values
    assert result.sel(categories="c").drop_vars("categories").equals(ex_result)

def test_add_category_where_validation():
    classes = ["a", "b"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "class": classes,
    }
    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(classes))
    da = xr.DataArray(data, coords=coords)
    land = LandDataArray(da)

    # Valid x/y boolean mask should pass
    valid_where = xr.DataArray(
        np.array([[True, False], [False, True], [True, True]]),
        dims=["x", "y"],
        coords={"x": coords["x"], "y": coords["y"]},
    )
    result = land.add_category("c", category_value=1, mask=valid_where)
    assert "c" in result["class"].values

    # Missing spatial dimensions should fail
    invalid_where_dims = xr.DataArray(
        np.array([True, False]),
        dims=["x"],
        coords={"x": coords["x"][:2]})
    
    with pytest.raises(ValueError):
        land.add_category("d", category_value=1, mask=invalid_where_dims)

    # Misaligned x coordinate should fail
    invalid_where_coords = xr.DataArray(
        np.array([[True, False], [False, True], [True, True]]),
        dims=["x", "y"],
        coords={"x": [10, 11, 12], "y": coords["y"]},
    )
    with pytest.raises(ValueError):
        land.add_category("e", category_value=1, mask=invalid_where_coords)

def test_add_category_existing_categories_error():
    categories = ["a", "b"]
    coords = {
        "x": [0, 1],
        "y": [0, 1],
        "class": categories,
    }
    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    da = xr.DataArray(data, coords=coords)
    land = LandDataArray(da)

    with pytest.raises(ValueError):
        land.add_category(["b"], category_value=1)

def test_add_category_duplicate_input_categories_error():
    classes = ["a", "b"]
    coords = {
        "x": [0, 1],
        "y": [0, 1],
        "class": classes,
    }
    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(classes))
    da = xr.DataArray(data, coords=coords)
    land = LandDataArray(da)


    with pytest.raises(ValueError):
        land.add_category(["c", "c"], category_value=1)