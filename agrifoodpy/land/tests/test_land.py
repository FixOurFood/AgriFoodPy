import numpy as np
import xarray as xr
from agrifoodpy.land.land import LandDataArray
import pytest
import matplotlib.pyplot as plt

def test_area_by_type():
    
    data = np.tile((np.arange(3, dtype=float)), (4,1))

    da = xr.DataArray(data=data, name="land",
                    coords={"x": [0, 1, 2, 3], "y": [0, 1, 2]})

    land = LandDataArray(da)
    # Test area by type without explicit values
    expected_result_no_values = np.array([4,4,4])
    result_no_values = land.area_by_type()
    
    assert(np.array_equal(expected_result_no_values, result_no_values))
    assert(list(result_no_values.coords) == ["land"])

    # Test area by type with explicit values
    expected_result_values = np.array([4,4])
    result_values = land.area_by_type(values=[1,2])
    
    assert(np.array_equal(expected_result_values, result_values))
    assert(list(result_values.coords) == ["land"])

    # Test area by type with explicit dimension name
    dim_name = "area"
    expected_result_dims = np.array([4,4,4])
    result_dims = land.area_by_type(dim=dim_name)
    
    assert(np.array_equal(expected_result_dims, result_dims))
    assert(list(result_dims.coords) == [dim_name])

    # Test area by type with nan values
    da_nan = da.copy(deep=True)
    da_nan[-1, -1] = np.nan
    da_nan.name = "land_nan"
    land_nan = LandDataArray(da_nan)

    expected_result_nan = np.array([4,4,3])
    result_nan = land_nan.area_by_type()

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

    # Test area overlap without explicit values

    expected_results_no_values = np.ones((3,4))
    result_no_values = land_left.area_overlap(da_right)

    assert(np.array_equal(expected_results_no_values, result_no_values))
    assert(list(result_no_values.coords) == [name_left, name_right])

    # Test area overlap with explicit values
    input_values_left = [1,2]
    input_values_right = [2,3]

    expected_results_values = np.ones((2,2))
    result_values = land_left.area_overlap(da_right,
                                           values_left=input_values_left,
                                           values_right=input_values_right)
    
    assert(np.array_equal(expected_results_no_values, result_no_values))
    assert(np.array_equal(result_no_values.coords, [name_left, name_right]))
    assert(np.array_equal(result_values[name_left].values, input_values_left))
    assert(np.array_equal(result_values[name_right].values, input_values_right))

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
    result_values_left = land_left.category_match(da_right, values_left=1)
    assert result_values_left.where(result_values_left==1).equals(da_left.where(da_left==1))
    assert np.all(result_values_left.where(result_values_left!=1).isnull())

    # Example with values on right map
    result_values_left = land_left.category_match(da_right, values_right=1)
    
    # Example with multiple values on both maps
    result_multivar = land_left.category_match(da_right,
                                               values_left=[0,1],
                                               values_right=[1,2])

    non_nan_values = result_multivar.where(~np.isnan(result_multivar),
                                           drop=True)
    truth = np.array([[0., 1.], [0., 1.]])
    assert np.array_equal(non_nan_values, truth)
    assert np.array_equal(non_nan_values.x.values, [1, 2])
    assert np.array_equal(non_nan_values.y.values, [0, 1])
    assert result_multivar.name == name_left

    # Example with non-matching values
    result_non_matching = land_left.category_match(da_right, values_left=4)
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
    result_no_coord = land.dominant_class()
    assert result_no_coord.equals(da.idxmax(dim="class"))

    # Test dominant class with coord name
    result_coord = land.dominant_class(class_coord="class")
    assert result_coord.equals(da.idxmax(dim="class"))

    # Test dominant class with non-matching coord name
    with pytest.raises(KeyError):
        result_non_matching = land.dominant_class(class_coord="non_matching")

    # Test with return index set to True
    result_return_index = land.dominant_class(return_index=True)
    result_return_index_truth = xr.DataArray(np.argmax(data, axis=2),
                                             coords=coords_index)

    assert result_return_index.equals(result_return_index_truth)