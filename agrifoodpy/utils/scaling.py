"""Scaling utilities module"""

import numpy as np
import xarray as xr


def logistic_scale(y0, y1, y2, y3, c_init, c_end):
    """
    Create an xarray DataArray with a logistic growth interval

    Parameters:
        y0 : (int)
            The initial year.
        y1 : (int)
            The year when the values start to transition.
        y2 : (int)
            The year when the transition completes.
        y3 : (int)
            The final year.
        c_init : (float)
            The initial constant value.
        c_end : (float)
            The final constant value.

    Returns: xarray DataArray
        An xarray DataArray object with 'year' as the coordinate and values set
        by a logistic growth between the user defined intervals.
    """

    # Create arrays and set values between y0 and y1 to c_init
    years = np.arange(y0, y3+1)
    values = np.ones_like(years, dtype=float) * c_init

    # Set values between y1 and y2 using a logistic curve
    var_segment = np.logical_and(years >= y1, years < y2)
    t = (years[var_segment] - y1) / (y2 - y1)
    values[var_segment] = c_init \
        + (c_end - c_init)*(1 / (1 + np.exp(-10 * (t - 0.5))))

    # Set values between y2 and y3 to c_end
    values[years >= y2] = c_end

    data_array = xr.DataArray(values, dims='Year', coords={'Year': years})
    return data_array


def linear_scale(y0, y1, y2, y3, c_init, c_end):
    """
    Create an xarray DataArray with a single coordinate called 'year'.

    The values from the first year 'y0' up to a given year 'y1' will be
    constant, then they will vary linearly between 'y1' and another given year
    'y2', and from 'y2' until the end of the array 'y3', the values will
    continue with a constant value.

    Parameters:
        y0 : (int)
            Starting year.
        y1 : (int)
            Year where the linear variation starts.
        y2 : (int)
            Year where the linear variation ends.
        y3 : (int)
            Last year in the array.
        c_init : (float)
            Value to use for initial constant scale segment.
        c_end : (float)

    Returns: xr.DataArray
        An xarray DataArray object with 'year' as the coordinate and values set
        by a linear growth between the user defined intervals.
    """

    # Create arrays and set values between y0 and y1 to c_init
    years = np.arange(y0, y3 + 1)
    values = np.ones_like(years, dtype=float) * c_init

    # Set values between y1 and y2 using straight line.
    var_segment = np.logical_and(years >= y1, years < y2)
    if y2 == y1:
        slope = c_end - c_init
    else:
        slope = float((c_end - c_init) / (y2 - y1))
    values[var_segment] = slope * (years[var_segment] - y1) + c_init

    # Set values between y2 and y3 to c_end
    values[years >= y2] = c_end

    data_array = xr.DataArray(values, coords={'Year': years}, dims=['Year'])

    return data_array
