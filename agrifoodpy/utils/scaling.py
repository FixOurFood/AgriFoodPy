"""Scaling utilities module"""

import numpy as np
import xarray as xr


def _validate_non_decreasing_years(years):
    """Validate that years are in non-decreasing order."""

    if not all(earlier <= later for earlier, later in zip(years, years[1:])):
        raise ValueError("Years must be in ascending order.")


def logistic_scale(y0, y1, y2, y3, c_init, c_end):
    """
    Create an xarray DataArray with a logistic growth interval

    The returned DataArray contains values that remain constant at c_init from
    year y0 to y1, then transition following a logistic curve from c_init to
    c_end between years y1 and y2, and finally remain constant at c_end from
    year y2 to y3.

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
        An xarray DataArray object with 'Year' as the coordinate and values set
        by a logistic growth between the user defined intervals.
    """

    _validate_non_decreasing_years([y0, y1, y2, y3])

    # Create arrays and set values between y0 and y1 to c_init
    years = np.arange(y0, y3+1)
    values = np.ones_like(years, dtype=float) * c_init

    # Set values between y1 and y2 using a logistic curve
    if y1 < y2:
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
    Create an xarray DataArray with a linear growth interval.

    The returned DataArray contains values that remain constant at c_init from
    year y0 to y1, then transition linearly from c_init to c_end between years
    y1 and y2, and finally remain constant at c_end from year y2 to y3.

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
        An xarray DataArray object with 'Year' as the coordinate and values set
        by a linear growth between the user defined intervals.
    """

    return piecewise_linear_scale(
        years=[y0, y1, y2, y3],
        values=[c_init, c_init, c_end, c_end]
        )

def piecewise_linear_scale(years, values):
    """
    Create an xarray DataArray with a piecewise linear scale.

    The returned DataArray contains values that transition linearly between
    specified years and values.

    Parameters:
        years : (list of int)
            A list of years where the values change.
        values : (list of float)
            A list of values corresponding to each year in the 'years' list.

    Returns: xr.DataArray
        An xarray DataArray object with 'Year' as the coordinate and values set
        by a piecewise linear scale between the user defined intervals.
    """

    if len(years) != len(values):
        raise ValueError("Length of 'years' and 'values' must be the same.")

    _validate_non_decreasing_years(years)

    # Create arrays for the full range of years
    full_years = np.arange(years[0], years[-1] + 1)
    full_values = np.zeros_like(full_years, dtype=float)

    # Fill in the values for each segment
    for i in range(len(years) - 1):
        var_segment = np.logical_and(
            full_years >= years[i],
            full_years < years[i + 1]
            )
        
        delta_years = years[i + 1] - years[i]
        if delta_years == 0:
            continue

        slope = (values[i + 1] - values[i]) / delta_years

        full_values[var_segment] = (slope
                                    *(full_years[var_segment] - years[i])
                                    +values[i])

    # Set the value for the last year
    full_values[full_years >= years[-1]] = values[-1]

    data_array = xr.DataArray(
        full_values,
        coords={'Year': full_years},
        dims=['Year']
        )

    return data_array

def piecewise_constant_scale(years, values):
    """
    Create an xarray DataArray with a piecewise constant scale.

    The returned DataArray contains values that remain constant between
    specified years and values.

    Parameters:
        years : (list of int)
            A list of years where the values change.
        values : (list of float)
            A list of values corresponding to each year in the 'years' list.

    Returns: xr.DataArray
        An xarray DataArray object with 'Year' as the coordinate and values set
        by a piecewise constant scale between the user defined intervals.
    """

    if len(years) != len(values):
        raise ValueError("Length of 'years' and 'values' must be the same.")

    _validate_non_decreasing_years(years)

    # Create arrays for the full range of years
    full_years = np.arange(years[0], years[-1] + 1)
    full_values = np.zeros_like(full_years, dtype=float)

    # Fill in the values for each segment
    for i in range(len(years) - 1):
        var_segment = np.logical_and(
            full_years >= years[i],
            full_years < years[i + 1]
            )
        
        full_values[var_segment] = values[i]

    # Set the value for the last year
    full_values[full_years >= years[-1]] = values[-1]

    data_array = xr.DataArray(
        full_values,
        coords={'Year': full_years},
        dims=['Year']
        )

    return data_array

def step_scale(y0, y1, y2, c_init, c_end):
    """
    Create an xarray DataArray with a step function.

    The returned DataArray contains values that remain constant at c_init from
    year y0 to y1, then transition immediately to c_end at year y1 and remain
    constant at c_end thereafter.

    Parameters:
        y0 : (int)
            Starting year.
        y1 : (int)
            Year where the step change occurs.
        y2 : (int)
            Last year in the array.
        c_init : (float)
            Value to use for initial constant scale segment.
        c_end : (float)
            Value to use for final constant scale segment.

    Returns: xr.DataArray
        An xarray DataArray object with 'Year' as the coordinate and values set
        by a step change between the user defined intervals.
    """

    return piecewise_constant_scale(
        years=[y0, y1, y2],
        values=[c_init, c_end, c_end]
        )

def pulse_scale(y0, y1, y2, y3, c_init, c_pulse):
    """
    Create an xarray DataArray with a pulse function.

    The returned DataArray contains values that remain constant at c_init from
    year y0 to y1, then transition immediately to c_pulse at year y1 and remain
    constant at c_pulse until year y2, after which it transitions back to
    c_init and remains constant at c_init until year y3.

    Parameters:
        y0 : (int)
            Starting year.
        y1 : (int)
            Year where the pulse starts.
        y2 : (int)
            Year where the pulse ends.
        y3 : (int)
            Last year in the array.
        c_init : (float)
            Value to use for initial and final constant scale segments.
        c_pulse : (float)
            Value to use for the pulse segment.

    Returns: xr.DataArray
        An xarray DataArray object with 'Year' as the coordinate and values set
        by a pulse function between the user defined intervals.
    """

    return piecewise_constant_scale(
        years=[y0, y1, y2, y3],
        values=[c_init, c_pulse, c_init, c_init]
        )


def piecewise_smoothstep_scale(years, values, smoother=False):
    """
    Create an xarray DataArray with a piecewise smoothstep scale.

    The returned DataArray contains values that transition smoothly between
    specified years and values using a smoothstep function.

    Parameters:
        years : (list of int)
            A list of years where the values change.
        values : (list of float)
            A list of values corresponding to each year in the 'years' list.
        smoother : (bool), optional
            If True, use a smoother 5th-degree polynomial smoothstep;
            otherwise use the standard smoothstep.

    Returns: xr.DataArray
        An xarray DataArray object with 'Year' as the coordinate and values set
        by a piecewise smoothstep scale between the user defined intervals.
    """

    if len(years) != len(values):
        raise ValueError("Length of 'years' and 'values' must be the same.")

    _validate_non_decreasing_years(years)

    # Create arrays for the full range of years
    full_years = np.arange(years[0], years[-1] + 1)
    full_values = np.zeros_like(full_years, dtype=float)

    # Fill in the values for each segment
    for i in range(len(years) - 1):
        var_segment = np.logical_and(
            full_years >= years[i],
            full_years < years[i + 1]
            )
        
        delta_years = years[i + 1] - years[i]
        if delta_years == 0:
            continue

        t = (full_years[var_segment] - years[i]) / delta_years

        if smoother:
            # Use a smoother smoothstep function (5th degree polynomial)
            smoothstep = t**3 * (t * (t * 6 - 15) + 10)
        else:
            smoothstep = t**2 * (3 - 2 * t)

        full_values[var_segment] = (values[i]
                                    + (values[i + 1] - values[i]) * smoothstep)

    # Set the value for the last year
    full_values[full_years >= years[-1]] = values[-1]

    data_array = xr.DataArray(
        full_values,
        coords={'Year': full_years},
        dims=['Year']
        )

    return data_array

def smoothstep_scale(y0, y1, y2, y3, c_init, c_end, smoother=False):
    """
    Create an xarray DataArray with a smoothstep function.

    The returned DataArray contains values that remain constant at c_init from
    year y0 to y1, then transition smoothly to c_end between years y1 and y2,
    and finally remain constant at c_end from year y2 to y3.

    Parameters:
        y0 : (int)
            Starting year.
        y1 : (int)
            Year where the smooth transition starts.
        y2 : (int)
            Year where the smooth transition ends.
        y3 : (int)
            Last year in the array.
        c_init : (float)
            Value to use for initial constant scale segment.
        c_end : (float)
            Value to use for final constant scale segment.
    
    Returns: xr.DataArray
        An xarray DataArray object with 'Year' as the coordinate and values set
        by a smoothstep function between the user defined intervals.
    """

    return piecewise_smoothstep_scale(
        years=[y0, y1, y2, y3],
        values=[c_init, c_init, c_end, c_end],
        smoother=smoother
        )