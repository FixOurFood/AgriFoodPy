import numpy as np
from agrifoodpy.utils.scaling import linear_scale, logistic_scale


def test_logistic_scale():

    # Basic functionality test
    y0, y1, y2, y3 = 2000, 2005, 2010, 2015
    c_init, c_end = 0, 10
    basic_result = logistic_scale(y0, y1, y2, y3, c_init, c_end)

    truth = [0, 0, 0, 0, 0,
             0.06692851, 0.47425873, 2.68941421, 7.31058579, 9.52574127,
             10, 10, 10, 10, 10, 10]

    assert np.allclose(basic_result, truth)
    assert np.array_equal(basic_result["Year"].values, np.arange(2000, 2016))

    # Negative values test
    y0, y1, y2, y3 = 2000, 2005, 2010, 2015
    c_init, c_end = -1, -10
    negative_result = logistic_scale(y0, y1, y2, y3, c_init, c_end)
    truth = [-1, -1, -1, -1, -1,
             -1.06023566, -1.42683286, -3.42047279, -7.57952721, -9.57316714,
             -10, -10, -10, -10, -10, -10]

    assert np.allclose(negative_result, truth)

    # Instant change test
    y0, y1, y2, y3 = 2000, 2001, 2001, 2015
    c_init, c_end = 0, 10
    instant_change_result = logistic_scale(y0, y1, y2, y3, c_init, c_end)

    assert instant_change_result[0] == 0
    assert instant_change_result[1] == 10

    # Change from first year
    y0, y1, y2, y3 = 2000, 2000, 2000, 2015
    c_init, c_end = 0, 10
    change_first_year = logistic_scale(y0, y1, y2, y3, c_init, c_end)

    assert np.array_equal(change_first_year, c_end * np.ones(y3+1-y0))

    # Constant value
    y0, y1, y2, y3 = 2000, 2000, 2000, 2015
    c_init, c_end = 5.5, 5.5
    constant_value = logistic_scale(y0, y1, y2, y3, c_init, c_end)

    assert np.array_equal(constant_value, c_init * np.ones(y3+1-y0))
    assert np.array_equal(constant_value, c_end * np.ones(y3+1-y0))


def test_linear_scale():

    # Basic functionality test
    basic_result = linear_scale(2000, 2005, 2010, 2015, 0, 10)
    truth = [0, 0, 0, 0, 0, 0, 2, 4, 6, 8, 10, 10, 10, 10, 10, 10]

    assert np.allclose(basic_result, truth)
    assert np.array_equal(basic_result["Year"].values, np.arange(2000, 2016))

    # Negative values test
    y0, y1, y2, y3 = 2000, 2005, 2010, 2015
    c_init, c_end = -1, -10
    negative_result = linear_scale(y0, y1, y2, y3, c_init, c_end)
    truth = [-1, -1, -1, -1, -1, -1, -2.8, -4.6, -6.4, -8.2,
             -10., -10., -10., -10., -10., -10.]

    assert np.allclose(negative_result, truth)

    # Instant change test
    y0, y1, y2, y3 = 2000, 2001, 2001, 2015
    c_init, c_end = 0, 10
    instant_change_result = linear_scale(y0, y1, y2, y3, c_init, c_end)

    assert instant_change_result[0] == 0
    assert instant_change_result[1] == 10

    # Change from first year
    y0, y1, y2, y3 = 2000, 2000, 2000, 2015
    c_init, c_end = 0, 10
    change_first_year = linear_scale(y0, y1, y2, y3, c_init, c_end)

    assert np.array_equal(change_first_year, c_end * np.ones(y3+1-y0))

    # Constant value
    y0, y1, y2, y3 = 2000, 2000, 2000, 2015
    c_init, c_end = 5.5, 5.5
    constant_value = linear_scale(y0, y1, y2, y3, c_init, c_end)

    assert np.array_equal(constant_value, c_init * np.ones(y3+1-y0))
    assert np.array_equal(constant_value, c_end * np.ones(y3+1-y0))
