import numpy as np
import xarray as xr

def test_fbs_impacts():

    from agrifoodpy.impact.model import fbs_impacts

    # Basic test
    items = ["Beef", "Apples"]
    years = [2020, 2021]

    fbs = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[10, 20], [30, 40]]),
            exports=(["Year", "Item"], [[5, 10], [15, 20]]),
            production=(["Year", "Item"], [[50, 60], [70, 80]])
            ),

    coords=dict(Item=("Item", items), Year=("Year", years))
    )

    impact = xr.DataArray([100, 0.5], dims=("Item"), coords={"Item": items})

    result = fbs_impacts(fbs, impact)

    truth = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[1000, 10], [3000, 20]]),
            exports=(["Year", "Item"], [[500, 5], [1500, 10]]),
            production=(["Year", "Item"], [[5000, 30], [7000, 40]])
            ),
        coords=dict(Item=("Item", items), Year=("Year", years))
    )

    assert result.equals(truth)

    # Test with population
    population = xr.DataArray(
        data = [1.0e6, 1.1e6],
        dims= ("Year"),
        coords={"Year": years})

    result = fbs_impacts(fbs, impact, population=population)

    truth = xr.Dataset(
        data_vars=dict(
            imports=(["Year", "Item"], [[1e9, 1e7], [3.3e9, 2.2e7]]),
            exports=(["Year", "Item"], [[5e8, 5e6], [1.65e9, 1.1e7]]),
            production=(["Year", "Item"], [[5e9, 3e7], [7.7e9, 4.4e7]])
            ),
        coords=dict(Item=("Item", items),
                    Year=("Year", years))
        )
        
    assert result.equals(truth)

    # Test summing over dimensions

    sum_dims = ["Item"]

    result = fbs_impacts(fbs, impact, sum_dims=sum_dims)

    truth = xr.Dataset(
        data_vars=dict(
            imports=(["Year"], [1.01e3, 3.02e3]),
            exports=(["Year"], [5.05e2, 1.51e3]),
            production=(["Year"], [5.03e3, 7.04e3])
            ),
        coords=dict(Year=("Year", years))
        )
        
    assert result.equals(truth)

def test_fair_interface():

    from agrifoodpy.impact.model import fair_co2_only

    # Test with single emission

    emissions = xr.DataArray(10, coords={"Year":2015})

    T, C, F = fair_co2_only(emissions=emissions)

    T_truth = xr.DataArray([0.0, 0.00133196], 
                           coords={"timebounds":[2014.5, 2015.5]})
    C_truth = xr.DataArray([278.3, 279.3534663],
                           coords={"timebounds":[2014.5, 2015.5]})
    F_truth = xr.DataArray([0.0, 0.02122413],
                           coords={"timebounds":[2014.5, 2015.5]})

    xr.testing.assert_allclose(T, T_truth)
    xr.testing.assert_allclose(C, C_truth)
    xr.testing.assert_allclose(F, F_truth)

    # Test with multiple emission values

    emissions = xr.DataArray(np.repeat(35, 10),
                             coords={"Year":np.arange(2010,2020)})

    T, C, F = fair_co2_only(emissions=emissions)

    T_truth = xr.DataArray([0.        , 0.00464001, 0.01451917, 0.02775184,
                            0.04310335, 0.05982477, 0.07744928, 0.09567989,
                            0.11432504, 0.13325952, 0.15239999],
                        coords={"timebounds":np.linspace(2009.5, 2019.5, 11)})

    C_truth = xr.DataArray([278.3       , 281.98713205, 284.96432983,
                            287.67924614, 290.23401333, 292.66883373,
                            295.00890336, 297.27301864, 299.47583696,
                            301.62892913, 303.74148527],
                        coords={"timebounds":np.linspace(2009.5, 2019.5, 11)})

    F_truth = xr.DataArray([0.        , 0.07393624, 0.13293446, 0.18620025,
                            0.23586687, 0.28279642, 0.32753321, 0.37048144,
                            0.41195413, 0.45219685, 0.4914037],
                        coords={"timebounds":np.linspace(2009.5, 2019.5, 11)})

    xr.testing.assert_allclose(T, T_truth)
    xr.testing.assert_allclose(C, C_truth)
    xr.testing.assert_allclose(F, F_truth)
