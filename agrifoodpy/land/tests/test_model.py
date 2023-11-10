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