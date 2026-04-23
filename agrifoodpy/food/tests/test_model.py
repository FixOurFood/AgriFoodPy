import numpy as np
import xarray as xr

import warnings

def test_balanced_scaling():

    from agrifoodpy.food.model import balanced_scaling

    items = ["Beef", "Apples"]
    years = [2020, 2021]

    fbs = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            food=(["Year", "Item"], [[55., 70.], [85., 100.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    # Test basic result
    result_basic = balanced_scaling(
        fbs,
        scale=1.0,
        element="food"
    )

    xr.testing.assert_equal(result_basic, fbs)

    # Test without year dimension
    fbs_no_year = fbs.isel(Year=0).drop_vars("Year")

    result_no_year = balanced_scaling(
        fbs_no_year,
        scale=2.0,
        element="food"
    )

    ex_result_no_year = xr.Dataset(
        data_vars=dict(
            imports=(["Item"], [10., 20.]),
            production=(["Item"], [50., 60.]),
            exports=(["Item"], [5., 10.]),
            food=(["Item"], [110., 140.])
            ),
        coords=dict(Item=("Item", items))
    )

    xr.testing.assert_equal(result_no_year, ex_result_no_year)

    # Test result with scalar scaling factor
    result_scalar = balanced_scaling(
        fbs,
        scale=2.0,
        element="food"
    )

    ex_result_scalar = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            food=(["Year", "Item"], [[110., 140.], [170., 200.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_equal(result_scalar, ex_result_scalar)

    # Test results with selected items
    result_items = balanced_scaling(
        fbs,
        scale=2.0,
        element="food",
        items="Beef"
    )

    ex_result_items = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            food=(["Year", "Item"], [[110., 70.], [170., 100.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_equal(result_items, ex_result_items)

    # Test results with selected items and setting constant to True
    result_constant = balanced_scaling(
        fbs,
        scale=2.0,
        element="food",
        items="Beef",
        constant=True
    )

    ex_result_constant = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            food=(["Year", "Item"], [[110., 15.], [170., 15.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_equal(result_constant, ex_result_constant)

    # Test selected items, constant to True, origin from "production" 
    result_origin = balanced_scaling(
        fbs,
        scale=2.0,
        element="food",
        items="Beef",
        constant=True,
        origin="production"
    )

    ex_result_origin = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            # production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            production=(["Year", "Item"], [[105., 5.], [155., -5.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            # food=(["Year", "Item"], [[55., 70.], [85., 100.]])
            food=(["Year", "Item"], [[110., 15.], [170., 15.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_equal(result_origin, ex_result_origin)

    # Test with fallback
    result_fallback = balanced_scaling(
        fbs,
        scale=2.0,
        element="food",
        items="Beef",
        constant=True,
        origin="production",
        fallback="imports"
    )

    ex_result_fallback = xr.Dataset(
        data_vars=dict(
            # imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            imports=(["Year", "Item"], [[10., 20.], [30., 45.]]),
            # production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            production=(["Year", "Item"], [[105., 5.], [155., 0.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            # food=(["Year", "Item"], [[55., 70.], [85., 100.]])
            food=(["Year", "Item"], [[110., 15.], [170., 15.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_equal(result_fallback, ex_result_fallback)
    
    # Test selected items, constant to True, origin from "exports"
    # add_to_origin set to False 
    result_add_origin = balanced_scaling(
        fbs,
        scale=2.0,
        element="food",
        items="Beef",
        constant=True,
        origin="exports",
        add_to_origin=False
    )

    ex_result_add_origin = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            # exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            exports=(["Year", "Item"], [[-50., 65.], [-70., 105.]]),
            # food=(["Year", "Item"], [[55., 70.], [85., 100.]])
            food=(["Year", "Item"], [[110., 15.], [170., 15.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_equal(result_add_origin, ex_result_add_origin)


    # Test with multiple origins and separate elasticity values
    result_elasticity = balanced_scaling(
        fbs,
        scale=2.0,
        element="food",
        items="Beef",
        constant=True,
        origin=["production", "imports"],
        elasticity=[0.8, 0.2]
    )

    ex_result_elasticity = xr.Dataset(
        data_vars=dict(
            # imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            imports=(["Year", "Item"], [[21., 9.], [47., 23.]]),
            # production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            production=(["Year", "Item"], [[94., 16.], [138., 12.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            # food=(["Year", "Item"], [[55., 70.], [85., 100.]])
            food=(["Year", "Item"], [[110., 15.], [170., 15.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_equal(result_elasticity, ex_result_elasticity)

    # Test with a scaling array
    from agrifoodpy.utils.scaling import linear_scale

    scale_arr = linear_scale(
        2020,
        2020,
        2021,
        2021,
        c_init=1.0,
        c_end=2.0 
    )

    result_scale_arr = balanced_scaling(
        fbs,
        scale=scale_arr,
        element="food",
        items="Beef",
    )

    ex_result_scale_arr = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            food=(["Year", "Item"], [[55., 70.], [170., 100.]])
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_equal(result_scale_arr, ex_result_scale_arr)


def test_SSR():

    from agrifoodpy.food.model import SSR

    items = ["Beef", "Apples"]
    years = [2020, 2021]

    fbs = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]]),
            ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    # Test basic result on all items
    result_basic = SSR(fbs)
    ex_result_basic = xr.DataArray([0.88, 0.810810], dims=("Year"),
                                coords={"Year": years})

    xr.testing.assert_allclose(result_basic, ex_result_basic)

    # Test for an item subset
    result_subset = SSR(fbs, items="Beef")
    ex_result_subset = xr.DataArray([0.909090, 0.823529], dims=("Year"),
                                    coords={"Year": years})

    xr.testing.assert_allclose(result_subset, ex_result_subset)

    # Test per item
    result_peritem = SSR(fbs, per_item=True)
    ex_result_peritem = xr.DataArray([[0.909090, 0.857142], [0.823529, 0.8]],
                                    dims=(["Year", "Item"]),
                                    coords={"Year": years, "Item": items})

    xr.testing.assert_allclose(result_peritem, ex_result_peritem)

def test_IDR():

    from agrifoodpy.food.model import IDR

    items = ["Beef", "Apples"]
    years = [2020, 2021]

    fbs = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]]),
            ),
      
        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    # Test basic result on all items
    result_basic = IDR(fbs)
    ex_result_basic = xr.DataArray([0.24, 0.37837838], dims=("Year"),
                                   coords={"Year": years})
    
    xr.testing.assert_allclose(result_basic, ex_result_basic)

    # Test for an item subset
    result_subset = IDR(fbs, items="Beef")
    ex_result_subset = xr.DataArray([0.1818181, 0.352941], dims=("Year"),
                                    coords={"Year": years})
    
    xr.testing.assert_allclose(result_subset, ex_result_subset)

    # Test per item
    result_peritem = IDR(fbs, per_item=True)
    ex_result_peritem = xr.DataArray([[0.1818181, 0.285714], [0.352941, 0.4]],
                                     dims=(["Year", "Item"]),
                                     coords={"Year": years, "Item": items})
    
    xr.testing.assert_allclose(result_peritem, ex_result_peritem)

def test_fbs_convert():

    from agrifoodpy.food.model import fbs_convert

    items = ["Beef", "Apples"]
    years = [2020, 2021]

    fbs = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]]),
            ),
      
        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    # Test basic result
    result_basic = fbs_convert(fbs, convertion_arr=1.0)
    ex_result_basic = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]]),
        ),
        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_allclose(result_basic, ex_result_basic)

    # Test with a conversion array
    conversion_arr = xr.DataArray([1.0, 2.0], dims=["Item"], coords={"Item": items})
    result_conversion = fbs_convert(fbs, convertion_arr=conversion_arr)
    ex_result_conversion = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 40], [30, 80]]),
            exports=(["Year", "Item"], [[5, 20], [15, 40]]),
            production=(["Year", "Item"], [[50, 120], [70, 160]]),
        ),
        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_allclose(result_conversion, ex_result_conversion)

    # Test with a conversion factor
    result_factor = fbs_convert(fbs, convertion_arr=2.0)
    ex_result_factor = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[20, 40], [60, 80]]),
            exports=(["Year", "Item"], [[10, 20], [30, 40]]),
            production=(["Year", "Item"], [[100, 120], [140, 160]]),
        ),
        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    xr.testing.assert_allclose(result_factor, ex_result_factor)


def test_scale_above_threshold():

    from agrifoodpy.food.model import scale_above_threshold
    from agrifoodpy.pipeline import Pipeline

    items = ["Beef", "Apples"]
    years = [2020, 2021]

    fbs = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10., 20.], [30., 40.]]),
            production=(["Year", "Item"], [[50., 60.], [70., 80.]]),
            exports=(["Year", "Item"], [[5., 10.], [15., 20.]]),
            food=(["Year", "Item"], [[55., 70.], [85., 100.]])
        ),

        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    # Test basic result with unity scaling factor
    result_basic = scale_above_threshold(
        fbs,
        scale=1.0,
        element="food",
    )

    xr.testing.assert_allclose(result_basic, fbs)

    # Test basic in a pipeline
    test_pipeline = Pipeline({"data": fbs})

    test_pipeline.add_node(
        scale_above_threshold,
        {
            "fbs": "data",
            "scale": 1.0,
            "element": "food",
        })

    test_pipeline.run()

    assert "scale_above_threshold" in test_pipeline.datablock
    xr.testing.assert_equal(
        test_pipeline.datablock["scale_above_threshold"], fbs)

    # Test result with positive scaling factor less than 1
    result_scaled = scale_above_threshold(
        fbs,
        scale=0.5,
        element="food",
        threshold=60.0
    )
    ex_result = (fbs["food"].sum(dim="Item") - 60.0) * 0.5 + 60.0
    
    xr.testing.assert_allclose(
        result_scaled["food"].sum(dim="Item"),
        ex_result)

    # Test result with positive scaling factor greater than 1
    result_scaled = scale_above_threshold(
        fbs,
        scale=2.0,
        element="food",
        threshold=60.0
    )
    ex_result = (fbs["food"].sum(dim="Item") - 60.0) * 2.0 + 60.0

    xr.testing.assert_allclose(result_scaled["food"].sum(dim="Item"),
                               ex_result)

    # Test result with zero scaling factor
    result_zero = scale_above_threshold(
        fbs,
        scale=0.0,
        element="food",
        threshold=60.0
    )
    ex_result_zero = (fbs["food"].sum(dim="Item") - 60.0) * 0.0 + 60.0
    xr.testing.assert_allclose(
        result_zero["food"].sum(dim="Item"),
        ex_result_zero)

    # Test result with array scale
    scale_arr = xr.DataArray(
        [0.1, 0.5],
        dims=["Year"],
        coords={"Year": years},
    )

    result_array_scale = scale_above_threshold(
        fbs,
        scale=scale_arr,
        element="food",
        threshold=60.0
    )

    ex_result_arr = (fbs["food"].sum(dim="Item") - 60.0) * scale_arr + 60.0
    xr.testing.assert_allclose(
        result_array_scale["food"].sum(dim="Item"),
        ex_result_arr)

    # Test with selected items
    result_array_items = scale_above_threshold(
        fbs,
        scale=0.0,
        element="food",
        threshold=60.0,
        items="Beef"
    )

    ex_result_sel = (fbs["food"].sum(dim="Item") - 60.0) * 0.0 + 60.0

    xr.testing.assert_allclose(
        result_array_items["food"].sum(dim="Item"),
        ex_result_sel)

    # Test with array threshold
    threshold_arr = xr.DataArray(
        [50.0, 70.0],
        dims=["Year"],
        coords={"Year": years},
    )

    result_array_threshold = scale_above_threshold(
        fbs,
        scale=0.5,
        element="food",
        threshold=threshold_arr
    )

    ex_result_threshold = (fbs["food"].sum(dim="Item") - threshold_arr) * 0.5 \
        + threshold_arr

    xr.testing.assert_allclose(
        result_array_threshold["food"].sum(dim="Item"),
        ex_result_threshold)

    # Test with origin
    result_origin = scale_above_threshold(
        fbs,
        scale=0.5,
        element="food",
        threshold=60.0,
        origin="production"
    )

    excess = fbs["food"] - result_origin["food"]
    ex_result_origin = fbs["production"] - excess
    xr.testing.assert_allclose(
        result_origin["production"], ex_result_origin)
    
    # Test with multiple origins and separate elasticity values
    result_elasticity = scale_above_threshold(
        fbs,
        scale=0.5,
        element="food",
        threshold=60.0,
        origin=["production", "imports"],
        elasticity=[0.8, 0.2]
    )

    excess = fbs["food"] - result_elasticity["food"]
    ex_result_prod = fbs["production"] - excess * 0.8
    ex_result_imports = fbs["imports"] - excess * 0.2

    xr.testing.assert_allclose(
        result_elasticity["production"], ex_result_prod)
    xr.testing.assert_allclose(
        result_elasticity["imports"], ex_result_imports)
    
    # Test with conversion array
    conversion_arr = xr.DataArray(
        [1.0, 2.0],
        dims=["Item"],
        coords={"Item": items})
    
    result_conversion = scale_above_threshold(
        fbs,
        scale=0.5,
        element="food",
        threshold=60.0,
        conversion_arr=conversion_arr
    )

    conv_arr = fbs * conversion_arr
    ex_result_conv = (conv_arr["food"].sum(dim="Item") - 60.0) * 0.5 + 60.0

    xr.testing.assert_allclose(
        (result_conversion["food"]*conversion_arr).sum(dim="Item"),
        ex_result_conv)


    
