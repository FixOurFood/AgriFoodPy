import numpy as np
import xarray as xr
from agrifoodpy.land.model import land_sequestration

def test_land_sequestration():

    # basic test with one category and one fraction
    lda = xr.DataArray([[0,1],[1,0]], coords={"x":[0,1], "y":[0,1]},
                       name = "land")
    
    result = land_sequestration(lda, 0, 0.5, 10)
    truth = xr.DataArray(data=10)

    xr.testing.assert_equal(result, truth)

    # test with multiple categories and one fraction
    result = land_sequestration(lda, [0,1], 0.5, 10)
    truth = xr.DataArray(data=20)

    xr.testing.assert_equal(result, truth)

    # test with multiple categories and multiple fractions
    result = land_sequestration(lda, [0,1], [0.5, 0.1], 10)
    truth = xr.DataArray(data=12)

    xr.testing.assert_equal(result, truth)

    # test with years value
    result = land_sequestration(lda, 0, 0.5, 10, years=10, growth_timescale=10)
    truth = xr.DataArray(data=np.arange(11), coords={"Year":np.arange(11)})

    xr.testing.assert_allclose(result, truth)

    # test with years array
    result = land_sequestration(lda, 0, 0.5, 10, years=np.arange(1960,2020),
                                growth_timescale=10)
    truth_data = np.concatenate((np.arange(11), np.ones(2020-1960-11)*10))
    truth = xr.DataArray(data=truth_data, coords={"Year":np.arange(1960, 2020)})

    xr.testing.assert_allclose(result, truth)

    # test with logistic growth function
    result = land_sequestration(lda, 0, 0.5, 10, years=10, growth_timescale=10,
                                growth="logistic")
    truth = xr.DataArray([0.06692851, 0.1798621 , 0.47425873, 1.19202922,
                        2.68941421, 5.        , 7.31058579, 8.80797078,
                        9.52574127, 9.8201379 , 10.],
                        coords={"Year":np.arange(11)})

    xr.testing.assert_allclose(result, truth)

# -----------------------------
# Tests for scale_land function
# -----------------------------

def test_scale_land_basic():
    # basic test with one category and one fraction

    from agrifoodpy.land.model import scale_land

    categories = ["Pasture", "Arable"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }

    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    land = xr.DataArray(data, coords=coords)

    fraction = np.random.rand()

    result = scale_land(land, origin="Pasture", fraction=fraction)

    truth = land.copy(deep=True)
    truth.loc[{"categories": "Pasture"}] *= fraction

    xr.testing.assert_allclose(result, truth)

def test_scale_land_multiple_categories():
    # test with multiple categories and one fraction

    from agrifoodpy.land.model import scale_land

    categories = ["Pasture", "Arable", "Forest"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }

    fraction = np.random.rand()

    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    land = xr.DataArray(data, coords=coords)

    result = scale_land(land, origin=["Pasture", "Arable"], fraction=fraction)

    truth = land.copy(deep=True)
    truth.loc[{"categories": ["Pasture", "Arable"]}] *= fraction

    xr.testing.assert_allclose(result, truth)

def test_scale_land_multiple_categories_multiple_fractions():
    # test with multiple categories and multiple fractions

    from agrifoodpy.land.model import scale_land

    categories = ["Pasture", "Arable", "Forest"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }

    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    land = xr.DataArray(data, coords=coords)

    fraction = xr.DataArray(
        np.random.rand(2),
        coords={"categories": ["Pasture", "Arable"]})

    result = scale_land(land, origin=["Pasture", "Arable"], fraction=fraction)

    truth = land.copy(deep=True)
    truth.loc[{"categories": "Pasture"}] *= fraction.loc[{"categories": "Pasture"}]
    truth.loc[{"categories": "Arable"}] *= fraction.loc[{"categories": "Arable"}]

    xr.testing.assert_allclose(result, truth)

def test_scale_land_single_target_category():
    # test with target category

    from agrifoodpy.land.model import scale_land

    categories = ["Pasture", "Arable", "Forest"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }

    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    land = xr.DataArray(data, coords=coords)

    fraction = np.random.rand()

    result = scale_land(
        land,
        origin="Pasture",
        fraction=fraction,
        keep_land_constant=True,
        target_category="Forest")

    truth = land.copy(deep=True)
    truth.loc[{"categories": "Pasture"}] *= fraction
    truth.loc[{"categories": "Forest"}] += \
        land.loc[{"categories": "Pasture"}] * (1-fraction)

    xr.testing.assert_allclose(result, truth)

def test_scale_land_multiple_target_categories():
    # Test with multiple target categories

    from agrifoodpy.land.model import scale_land

    categories = ["Pasture", "Arable", "Forest", "Urban"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }

    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    land = xr.DataArray(data, coords=coords)

    fraction = np.random.rand()

    result = scale_land(
        land,
        origin="Pasture",
        fraction=fraction,
        keep_land_constant=True,
        target_category=["Forest", "Urban"])
    
    truth = land.copy(deep=True)
    truth.loc[{"categories": "Pasture"}] *= fraction
    truth.loc[{"categories": ["Forest", "Urban"]}] += \
        land.loc[{"categories": "Pasture"}] * (1-fraction) / 2

    xr.testing.assert_allclose(result, truth)

def test_scale_land_multiple_target_categories_with_distribution():
    # Test with multiple target categories and target distribution

    from agrifoodpy.land.model import scale_land

    categories = ["Pasture", "Arable", "Forest", "Urban"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
    }

    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    land = xr.DataArray(data, coords=coords)

    fraction = np.random.rand()
    target_distr_arr = np.random.rand(2)
    target_distr_arr /= target_distr_arr.sum()
    target_distribution = xr.DataArray(
        target_distr_arr,
        coords={"categories": ["Forest", "Urban"]})

    result = scale_land(
        land,
        origin="Pasture",
        fraction=fraction,
        keep_land_constant=True,
        target_category=["Forest", "Urban"],
        target_distribution=target_distribution)
    
    truth = land.copy(deep=True)
    truth.loc[{"categories": "Pasture"}] *= fraction
    truth.loc[{"categories": "Forest"}] += land.loc[{"categories": "Pasture"}] \
        * (1-fraction) * target_distribution.loc[{"categories": "Forest"}]
    truth.loc[{"categories": "Urban"}] += land.loc[{"categories": "Pasture"}] \
        * (1-fraction) * target_distribution.loc[{"categories": "Urban"}]

    xr.testing.assert_allclose(result, truth)

def test_scale_land_time_dependent_scale():
    # Test with time dependent scale factor

    from agrifoodpy.land.model import scale_land

    categories = ["Pasture", "Arable", "Forest"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "categories": categories,
        "Year": [2000, 2010]
    }

    data = np.random.rand(
        len(coords["x"]),
        len(coords["y"]),
        len(categories),
        len(coords["Year"])
        )
    land = xr.DataArray(data, coords=coords)

    fraction = xr.DataArray(
        np.random.rand(len(coords["Year"])),
        coords={"Year": coords["Year"]})

    result = scale_land(
        land,
        origin="Pasture",
        fraction=fraction,
        keep_land_constant=True,
        target_category=["Arable", "Forest"],
        target_distribution=[0.75, 0.25])
    
    truth = land.copy(deep=True)
    for t in coords["Year"]:
        truth.loc[{"categories": "Pasture", "Year": t}] \
            *= fraction.loc[{"Year": t}]
        
        truth.loc[{"categories": "Arable", "Year": t}] \
            += land.loc[{"categories": "Pasture", "Year": t}] \
            * (1-fraction.loc[{"Year": t}]) * 0.75
        
        truth.loc[{"categories": "Forest", "Year": t}] \
            += land.loc[{"categories": "Pasture", "Year": t}] \
            * (1-fraction.loc[{"Year": t}]) * 0.25

    xr.testing.assert_allclose(result, truth)

def test_scale_land_custom_category_dim():
    # Test with custom category dimension

    from agrifoodpy.land.model import scale_land

    categories = ["Pasture", "Arable", "Forest"]
    coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "land_category": categories,
    }

    data = np.random.rand(len(coords["x"]), len(coords["y"]), len(categories))
    land = xr.DataArray(data, coords=coords)

    fraction = np.random.rand()

    result = scale_land(
        land,
        origin="Pasture",
        fraction=fraction,
        keep_land_constant=True,
        target_category=["Arable", "Forest"],
        target_distribution=[0.75, 0.25],
        category_dim="land_category")
    
    truth = land.copy(deep=True)
    truth.loc[{"land_category": "Pasture"}] \
        *= fraction
    
    truth.loc[{"land_category": "Arable"}] \
        += land.loc[{"land_category": "Pasture"}] * (1-fraction) * 0.75
    
    truth.loc[{"land_category": "Forest"}] \
        += land.loc[{"land_category": "Pasture"}] * (1-fraction) * 0.25

    xr.testing.assert_allclose(result, truth)

# --------------------------------
# Tests for land_scaling_from_food
# --------------------------------

def test_land_scaling_from_food_basic():
    # Basic test with unchanged food balance sheet and one category

    from agrifoodpy.land.model import land_scaling_from_food

    items = ["Beef", "Apples"]
    food_coords = {"Item": items}
    food_data = np.random.rand(len(food_coords["Item"]))

    fbs_obs = xr.Dataset(
        data_vars={"production": (["Item"], food_data)},
        coords=food_coords
    )
    
    fbs_ref = fbs_obs.copy(deep=True)

    categories = ["Pasture", "Arable", "Forest"]
    land_coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "category": categories,
    }

    land_data = np.random.rand(
        len(land_coords["x"]),
        len(land_coords["y"]),
        len(land_coords["category"]))

    land = xr.DataArray(land_data, coords=land_coords)

    result = land_scaling_from_food(
        land,
        fbs_obs,
        fbs_ref,
        element="production",
        category="Pasture")
    
    xr.testing.assert_allclose(result, land)

def test_land_scaling_from_food_basic_change():
    # Basic test with changed food balance sheet and one category

    from agrifoodpy.land.model import land_scaling_from_food

    items = ["Beef", "Apples"]
    food_coords = {"Item": items}
    food_data = np.random.rand(len(food_coords["Item"]))

    fbs_ref = xr.Dataset(
        data_vars={"production": (["Item"], food_data)},
        coords=food_coords
    )
    
    fbs_obs = fbs_ref.copy(deep=True)
    fbs_obs["production"] *= 2

    categories = ["Pasture", "Arable", "Forest"]
    land_coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "category": categories,
    }

    land_data = np.random.rand(
        len(land_coords["x"]),
        len(land_coords["y"]),
        len(land_coords["category"]))

    land = xr.DataArray(land_data, coords=land_coords)

    result = land_scaling_from_food(
        land,
        fbs_obs,
        fbs_ref,
        element="production",
        category="Pasture")
        
    truth = land.copy(deep=True)
    truth.loc[{"category":"Pasture"}] *= 2
    
    xr.testing.assert_allclose(result, truth)

def test_land_scaling_from_food_with_items():
    # Test with specified items

    from agrifoodpy.land.model import land_scaling_from_food

    items = ["Beef", "Apples"]
    food_coords = {"Item": items}
    food_data = np.random.rand(len(food_coords["Item"]))

    fbs_ref = xr.Dataset(
        data_vars={"production": (["Item"], food_data)},
        coords=food_coords
    )
    
    fbs_obs = fbs_ref.copy(deep=True)
    fbs_obs["production"].loc[{"Item":"Beef"}] *= 2

    categories = ["Pasture", "Arable", "Forest"]
    land_coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "category": categories,
    }

    land_data = np.random.rand(
        len(land_coords["x"]),
        len(land_coords["y"]),
        len(land_coords["category"]))

    land = xr.DataArray(land_data, coords=land_coords)

    result = land_scaling_from_food(
        land,
        fbs_obs,
        fbs_ref,
        element="production",
        category="Pasture",
        items=["Beef"])
    
    truth = land.copy(deep=True)
    truth.loc[{"category":"Pasture"}] *= 2
    
    xr.testing.assert_allclose(result, truth)


def test_land_scaling_from_food_with_target_categories():
    # Test with constant land and target categories

    from agrifoodpy.land.model import land_scaling_from_food

    items = ["Beef", "Apples"]
    food_coords = {"Item": items}
    food_data = np.random.rand(len(food_coords["Item"]))

    fbs_ref = xr.Dataset(
        data_vars={"production": (["Item"], food_data)},
        coords=food_coords
    )
    
    food_scale = np.random.rand() * 0.5 + 1
    fbs_obs = fbs_ref.copy(deep=True)
    fbs_obs["production"].loc[{"Item":"Beef"}] *= food_scale


    categories = ["Pasture", "Arable", "Forest"]
    land_coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "category": categories,
    }

    land_data = np.random.rand(
        len(land_coords["x"]),
        len(land_coords["y"]),
        len(land_coords["category"]))

    land = xr.DataArray(land_data, coords=land_coords)

    result = land_scaling_from_food(
        land,
        fbs_obs,
        fbs_ref,
        element="production",
        category="Pasture",
        keep_land_constant=True,
        target_category="Forest",
        items=["Beef"])
    
    truth = land.copy(deep=True)
    truth.loc[{"category":"Pasture"}] *= food_scale
    truth.loc[{"category":"Forest"}] -= land.loc[{"category":"Pasture"}] \
        * (food_scale - 1)
    
    xr.testing.assert_allclose(result, truth)


def test_land_scaling_from_food_with_target_categories_and_distribution():
    # Test with constant land, target categories and target distribution
    
    from agrifoodpy.land.model import land_scaling_from_food

    items = ["Beef", "Apples"]
    food_coords = {"Item": items}
    food_data = np.random.rand(len(food_coords["Item"]))

    fbs_ref = xr.Dataset(
        data_vars={"production": (["Item"], food_data)},
        coords=food_coords
    )
    
    food_scale = np.random.rand() * 0.5 + 1
    fbs_obs = fbs_ref.copy(deep=True)
    fbs_obs["production"].loc[{"Item":"Beef"}] *= food_scale


    categories = ["Pasture", "Arable", "Forest"]
    land_coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "category": categories,
    }

    land_data = np.random.rand(
        len(land_coords["x"]),
        len(land_coords["y"]),
        len(land_coords["category"]))

    land = xr.DataArray(land_data, coords=land_coords)

    result = land_scaling_from_food(
        land,
        fbs_obs,
        fbs_ref,
        element="production",
        category="Pasture",
        keep_land_constant=True,
        target_category=["Forest", "Arable"],
        target_distribution=[0.75, 0.25],
        items=["Beef"])
    
    truth = land.copy(deep=True)
    truth.loc[{"category":"Pasture"}] *= food_scale
    truth.loc[{"category":"Forest"}] -= land.loc[{"category":"Pasture"}] \
        * (food_scale - 1) * 0.75
    truth.loc[{"category":"Arable"}] -= land.loc[{"category":"Pasture"}] \
        * (food_scale - 1) * 0.25
    
    xr.testing.assert_allclose(result, truth)

def test_land_scaling_from_food_with_time_dependent_fbs():

    from agrifoodpy.land.model import land_scaling_from_food

    items = ["Beef", "Apples"]
    years = [2000, 2010]
    food_coords = {"Item": items, "Year": years}
    food_data = np.random.rand(
        len(food_coords["Item"]),
        len(food_coords["Year"])
        )

    fbs_ref = xr.Dataset(
        data_vars={"production": (["Item", "Year"], food_data)},
        coords=food_coords
    )
    
    food_scale = xr.DataArray(
            np.random.rand(len(years)),
            coords={"Year": years}
        ) * 0.5 + 1
    
    fbs_obs = fbs_ref.copy(deep=True)
    fbs_obs["production"].loc[{"Item":"Beef"}] *= food_scale

    categories = ["Pasture", "Arable", "Forest"]
    land_coords = {
        "x": [0, 1, 2],
        "y": [0, 1],
        "category": categories,
        "Year": years
    }

    land_data = np.random.rand(
        len(land_coords["x"]),
        len(land_coords["y"]),
        len(land_coords["category"]),
        len(land_coords["Year"])
        )

    land = xr.DataArray(land_data, coords=land_coords)

    result = land_scaling_from_food(
        land,
        fbs_obs,
        fbs_ref,
        element="production",
        category="Pasture",
        keep_land_constant=True,
        target_category="Forest",
        items=["Beef"])
    
    truth = land.copy(deep=True)
    truth.loc[{"category":"Pasture"}] *= food_scale
    truth.loc[{"category":"Forest"}] -= land.loc[{"category":"Pasture"}] \
        * (food_scale - 1)
    
    xr.testing.assert_allclose(result, truth)
