import numpy as np
import pytest
from agrifoodpy.utils.scaling import (
    linear_scale,
    logistic_scale,
    piecewise_constant_scale,
    piecewise_linear_scale,
    piecewise_smoothstep_scale,
    pulse_scale,
    smoothstep_scale,
    step_scale,
)

# ---------------------------------
# Tests for logistic_scale function
# ---------------------------------

def test_logistic_scale_basic():
    # Basic functionality test
    y0, y1, y2, y3 = 2000, 2005, 2010, 2015
    c_init, c_end = 0, 10
    basic_result = logistic_scale(y0, y1, y2, y3, c_init, c_end)

    truth = [0, 0, 0, 0, 0,
             0.06692851, 0.47425873, 2.68941421, 7.31058579, 9.52574127,
             10, 10, 10, 10, 10, 10]

    assert np.allclose(basic_result, truth)
    assert np.array_equal(basic_result["Year"].values, np.arange(2000, 2016))

def test_logistic_scale_negative():
    # Negative values test
    y0, y1, y2, y3 = 2000, 2005, 2010, 2015
    c_init, c_end = -1, -10
    negative_result = logistic_scale(y0, y1, y2, y3, c_init, c_end)
    truth = [-1, -1, -1, -1, -1,
             -1.06023566, -1.42683286, -3.42047279, -7.57952721, -9.57316714,
             -10, -10, -10, -10, -10, -10]

    assert np.allclose(negative_result, truth)

def test_logistic_scale_from_first_year():
    # Change from first year
    y0, y1, y2, y3 = 2000, 2000, 2000, 2015
    c_init, c_end = 0, 10
    change_first_year = logistic_scale(y0, y1, y2, y3, c_init, c_end)

    assert np.array_equal(change_first_year, c_end * np.ones(y3+1-y0))

def test_logistic_scale_constant_value():
    # Constant value
    y0, y1, y2, y3 = 2000, 2000, 2000, 2015
    c_init, c_end = 5.5, 5.5
    constant_value = logistic_scale(y0, y1, y2, y3, c_init, c_end)

    assert np.array_equal(constant_value, c_init * np.ones(y3+1-y0))
    assert np.array_equal(constant_value, c_end * np.ones(y3+1-y0))

def test_logistic_scale_immediate_transition():
    # y1 == y2 means no transition interval, so values jump to c_end at y1
    result = logistic_scale(2000, 2005, 2005, 2010, 0, 10)
    truth = [0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2011))

def test_logistic_scale_raises_for_decreasing_years():
    with pytest.raises(ValueError, match="Years must be in ascending order"):
        logistic_scale(2000, 2005, 2004, 2010, 0, 10)


# -------------------------------
# Tests for linear_scale function
# -------------------------------

def test_linear_scale():
    # Basic functionality test
    basic_result = linear_scale(2000, 2005, 2010, 2015, 0, 10)
    truth = [0, 0, 0, 0, 0, 0, 2, 4, 6, 8, 10, 10, 10, 10, 10, 10]

    assert np.allclose(basic_result, truth)
    assert np.array_equal(basic_result["Year"].values, np.arange(2000, 2016))

def test_linear_scale_negative():
    # Negative values test
    y0, y1, y2, y3 = 2000, 2005, 2010, 2015
    c_init, c_end = -1, -10
    negative_result = linear_scale(y0, y1, y2, y3, c_init, c_end)
    truth = [-1, -1, -1, -1, -1, -1, -2.8, -4.6, -6.4, -8.2,
             -10., -10., -10., -10., -10., -10.]

    assert np.allclose(negative_result, truth)

def test_linear_scale_from_first_year():
    # Change from first year
    y0, y1, y2, y3 = 2000, 2000, 2000, 2015
    c_init, c_end = 0, 10
    change_first_year = linear_scale(y0, y1, y2, y3, c_init, c_end)

    assert np.array_equal(change_first_year, c_end * np.ones(y3+1-y0))

def test_linear_scale_constant_value():
    # Constant value
    y0, y1, y2, y3 = 2000, 2000, 2000, 2015
    c_init, c_end = 5.5, 5.5
    constant_value = linear_scale(y0, y1, y2, y3, c_init, c_end)

    assert np.array_equal(constant_value, c_init * np.ones(y3+1-y0))
    assert np.array_equal(constant_value, c_end * np.ones(y3+1-y0))

def test_linear_scale_start_immediately():
    # y0 == y1 should start linear growth immediately at y0
    result = linear_scale(2000, 2000, 2005, 2010, 0, 10)
    truth = [0, 2, 4, 6, 8, 10, 10, 10, 10, 10, 10]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2011))

def test_linear_scale_end_last_year():
    # y2 == y3 should still return a valid series ending at c_end
    result = linear_scale(2000, 2005, 2010, 2010, 0, 10)
    truth = [0, 0, 0, 0, 0, 0, 2, 4, 6, 8, 10]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2011))

def test_linear_scale_raises_for_decreasing_years():
    with pytest.raises(ValueError, match="Years must be in ascending order"):
        linear_scale(2000, 2005, 2004, 2010, 0, 10)


# --------------------------------------
# Tests for piecewise_linear_scale
# --------------------------------------

def test_piecewise_linear_scale_basic():
    result = piecewise_linear_scale([2000, 2003, 2005], [0, 6, 10])
    truth = [0, 2, 4, 6, 8, 10]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2006))


def test_piecewise_linear_scale_raises_for_mismatched_lengths():
    with pytest.raises(ValueError, match="Length of 'years' and 'values' must be the same"):
        piecewise_linear_scale([2000, 2005], [0])


def test_piecewise_linear_scale_raises_for_decreasing_years():
    with pytest.raises(ValueError, match="Years must be in ascending order"):
        piecewise_linear_scale([2000, 2005, 2004], [0, 1, 2])


# --------------------------------------
# Tests for piecewise_constant_scale
# --------------------------------------

def test_piecewise_constant_scale_basic():
    result = piecewise_constant_scale([2000, 2003, 2005], [1, 3, 7])
    truth = [1, 1, 1, 3, 3, 7]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2006))


def test_piecewise_constant_scale_raises_for_mismatched_lengths():
    with pytest.raises(ValueError, match="Length of 'years' and 'values' must be the same"):
        piecewise_constant_scale([2000, 2005], [1])


def test_piecewise_constant_scale_raises_for_decreasing_years():
    with pytest.raises(ValueError, match="Years must be in ascending order"):
        piecewise_constant_scale([2000, 2005, 2004], [1, 2, 3])


# --------------------------------------
# Tests for step_scale and pulse_scale
# --------------------------------------

def test_step_scale_basic():
    result = step_scale(2000, 2003, 2005, 2, 9)
    truth = [2, 2, 2, 9, 9, 9]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2006))


def test_step_scale_immediate_transition():
    result = step_scale(2000, 2000, 2003, 2, 9)
    truth = [9, 9, 9, 9]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2004))


def test_pulse_scale_basic():
    result = pulse_scale(2000, 2002, 2004, 2006, 1, 5)
    truth = [1, 1, 5, 5, 1, 1, 1]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2007))


# --------------------------------------
# Tests for piecewise_smoothstep_scale
# and smoothstep_scale
# --------------------------------------

def test_piecewise_smoothstep_scale_basic():
    result = piecewise_smoothstep_scale([2000, 2002], [0.0, 1.0])
    truth = [0.0, 0.5, 1.0]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2003))


def test_piecewise_smoothstep_scale_smoother_basic():
    result = piecewise_smoothstep_scale([2000, 2002], [0.0, 1.0], smoother=True)
    truth = [0.0, 0.5, 1.0]

    assert np.allclose(result, truth)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2003))


def test_piecewise_smoothstep_scale_raises_for_mismatched_lengths():
    with pytest.raises(ValueError, match="Length of 'years' and 'values' must be the same"):
        piecewise_smoothstep_scale([2000, 2005], [0.0])


def test_piecewise_smoothstep_scale_raises_for_decreasing_years():
    with pytest.raises(ValueError, match="Years must be in ascending order"):
        piecewise_smoothstep_scale([2000, 2005, 2004], [0.0, 0.5, 1.0])


def test_smoothstep_scale_wrapper_matches_piecewise():
    result = smoothstep_scale(2000, 2002, 2004, 2006, 1.0, 3.0)
    expected = piecewise_smoothstep_scale([2000, 2002, 2004, 2006], [1.0, 1.0, 3.0, 3.0])

    assert np.allclose(result, expected)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2007))


def test_smoothstep_scale_wrapper_matches_piecewise_smoother():
    result = smoothstep_scale(2000, 2002, 2004, 2006, 1.0, 3.0, smoother=True)
    expected = piecewise_smoothstep_scale(
        [2000, 2002, 2004, 2006],
        [1.0, 1.0, 3.0, 3.0],
        smoother=True,
    )

    assert np.allclose(result, expected)
    assert np.array_equal(result["Year"].values, np.arange(2000, 2007))

