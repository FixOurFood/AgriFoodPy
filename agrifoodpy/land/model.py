""" Module for land intervention models

"""

import numpy as np
from ..land.land import LandDataArray


def land_sequestration(
    land_da,
    use_id,
    fraction,
    max_seq,
    years=None,
    growth_timescale=10,
    growth="linear",
    ha_per_pixel=1
):

    """Additional land use sequestration model.

    Computes the anual additional sequestration from land use change as a
    function of the different land category converted fractional areas.

    Given a Land Data Array map with pixel id values for the different land use
    types, the model computes additional sequestration from land given the new
    value in [t CO2e / yr].

    Parameters
    ----------
    land : xarray.Dataarray
        Input land array containing the id id value with the dominant land use
        type on that pixel.
    use_id : int, array
        Land category identifiers for the land uses to be converted.
    fraction : float, array
        Fraction of each repurposed land category
    max_seq : float
        Maximum sequestration achieved at the end of the growth period in
        [t CO2e / yr]
    growth : str
        Type of sequestration growth. Can be one of "linear" and "logistic"
    growth_timescale : float
        Time in years for land to reach full sequestration potential max_seq
    years : int, array
        Year range length, or array of years for which the sequestration is
        computed. If not set, stationary maximum values are returned
    ha_per_pixel : float
        Area per pixel in hectares.

    Returns
    -------
    seq : xarray.DataArray
        DataArray with the per year sequestration
    """

    if np.isscalar(use_id):
        use_id = np.array(use_id)

    # If single scalar value, use the same for all categories
    if np.isscalar(fraction):
        fraction = np.ones_like(use_id)*fraction
    else:
        fraction = np.array(fraction)

    if not (fraction >= 0).all() and (fraction <= 1).all():
        raise ValueError("Input fraction values must be between 0 and 1")

    pixel_count_category = land_da.land.area_by_type(values=use_id)

    # area in hectares
    area_category = pixel_count_category * ha_per_pixel

    if growth == "linear":
        from agrifoodpy.utils.scaling import linear_scale as growth_shape
    elif growth == "logistic":
        from agrifoodpy.utils.scaling import logistic_scale as growth_shape
    else:
        raise ValueError("Growth must be one of 'linear' or 'logistic'")

    if years is not None:
        # single scalar value
        if np.isscalar(years):
            scale = growth_shape(0, 0, growth_timescale, years, 0, 1)
        # year range
        else:
            y0 = np.max((0, np.min(years)))
            y1 = np.max((0, np.min(years)))
            y2 = growth_timescale + y1
            y3 = np.max(years)
            scale = growth_shape(y0, y1, y2, y3, 0, 1)
    else:
        scale = 1

    # agroforestry
    area = area_category * fraction
    total_seq = area.sum() * scale * max_seq

    return total_seq
