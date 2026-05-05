""" Module for land intervention models
"""

import numpy as np
import xarray as xr
from ..land.land import LandDataArray
from ..pipeline import pipeline_node
from ..utils.dict_utils import item_parser 
import warnings

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

    pixel_count_category = land_da.land.area_by_category(categories=use_id)

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

@pipeline_node("land")
def scale_land(
    land,
    origin,
    fraction,
    keep_land_constant=False,
    target_category=None,
    target_distribution=None,
    category_dim=None,
):
    """Convert land from one category to another.

    Given a Land Data Array map with pixel values for the different land use
    types, the model computes the new land use map after conversion of a
    fraction of the per-pixel utilisation from a set of categories to a target
    category.

    Parameters
    ----------
    land : xarray.Dataarray
        Input land array containing the id id value with the dominant land use
        type on that pixel.
    origin : str, array
        Land category identifiers for the land uses to be converted.
    fraction : float, xarray.DataArray
        Conversion fraction of each repurposed land category. Can be a single
        scalar value, an array with the same length as the origin land
        categories, and optionally, include a time dimension for dynamic
        conversion.
    keep_land_constant : bool, optional
        If True, the total land area is kept constant by scaling the other
        categories proportionally to the change in the target category. If
        False, only the target category is scaled, allowing the total land area
        to change.
    target : str, optional
        Land category identifiers for the land use to convert to. If not
        provided, the converted land distributed across all non-origin
        categories.
    target_distribution : array-like, xarray.DataArray, optional
        Relative distribution used to allocate converted land across target
        categories. If array-like, it must have the same length as ``target``.
        If a DataArray, it must include ``category_dim`` with coordinates equal
        to ``target`` and can optionally include a ``Year`` dimension for
        time-varying distribution.    
    category_dim : str
        Name of the land category dimension in the input land DataArray.

    Returns
    -------
    new_land : xarray.DataArray
        DataArray with the new land use map after conversion.
    """

    if isinstance(origin, str):
        origin = [origin]


    # Use the first non spatial dimension if category dimension not provided
    if category_dim is None:
        category_dim = [d for d in land.dims if d not in ["Year", "x", "y"]][0]

    for orig in origin:
        if orig not in land[category_dim].values:
            raise ValueError(f"Origin category {orig} not found in land"
                             " categories")

    new_land = land.copy()

    # Validate fraction values
    if np.isscalar(fraction):
        if fraction < 0 or fraction > 1:
            warnings.warn("Fraction values must be between 0 and 1")
    else:
        if np.any((fraction < 0) | (fraction > 1)):
            warnings.warn("Fraction values must be between 0 and 1")

    # Scale land
    delta_land = land.sel({category_dim: origin}) * fraction

    new_land.loc[{category_dim: origin}] -= delta_land

    # If keeping land constant, distribute the converted land across targets
    if keep_land_constant:
        if target_category is None:
            target_category = [c for c in land[category_dim].values if c not in origin]

        elif isinstance(target_category, str):
            target_category = [target_category]            

        # Check that target class exist. If not, add them to the land categories
        for targ in target_category:
            if targ not in land[category_dim].values:
                new_land = new_land.land.add_category(targ, category_dim=category_dim)

        # Validate and normalize target distribution
        if target_distribution is None:
            target_distribution = np.ones(len(target_category), dtype=float)

        if isinstance(target_distribution, xr.DataArray):
            if category_dim not in target_distribution.dims:
                raise ValueError(
                    "target_distribution DataArray must include the category "
                    f"dimension '{category_dim}'"
                )

            extra_dims = set(target_distribution.dims) - {category_dim, "Year"}
            if extra_dims:
                raise ValueError(
                    "target_distribution DataArray supports only category and "
                    f"optional Year dimensions, got extra dimensions: {extra_dims}"
                )

            dist_categories = set(target_distribution[category_dim].values.tolist())
            target_categories = set(target_category)
            if dist_categories != target_categories:
                raise ValueError(
                    "target_distribution category coordinates must match target "
                    f"categories exactly. Expected {target_category}, got "
                    f"{list(target_distribution[category_dim].values)}"
                )

            target_distribution = target_distribution.sel({category_dim: target_category})

            if ((target_distribution < 0) | (~np.isfinite(target_distribution))).any():
                raise ValueError("target_distribution values must be finite and" \
                " non-negative")

            dist_sum = target_distribution.sum(dim=category_dim)
            if (dist_sum <= 0).any():
                raise ValueError(
                    "target_distribution must have a strictly positive total "
                    "across target categories"
                )

            target_distribution = target_distribution / dist_sum
        else:
            target_distribution = np.asarray(target_distribution, dtype=float)
            if target_distribution.ndim != 1 or target_distribution.size != len(target_category):
                raise ValueError(
                    "target_distribution must be a 1D array with the same length "
                    "as target"
                )

            if np.any((target_distribution < 0) | (~np.isfinite(target_distribution))):
                raise ValueError("target_distribution values must be finite and" \
                "non-negative")

            dist_sum = target_distribution.sum()
            if dist_sum <= 0:
                raise ValueError(
                    "target_distribution must have a strictly positive total "
                    "across target categories"
                )

            target_distribution = xr.DataArray(
                target_distribution / dist_sum,
                dims=[category_dim],
                coords={category_dim: target_category},
            )

        total_delta = delta_land.sum(dim=category_dim)
        distributed_delta = total_delta * target_distribution

        new_land.loc[{category_dim: target_category}] += distributed_delta.sel({category_dim: target_category})

    return new_land


@pipeline_node(["land", "fbs", "fbs_reference"])
def land_scaling_from_food(
    land,
    fbs,
    fbs_reference,
    element,
    category,
    items=None,
    category_dim=None,
    keep_land_constant=False,
    target_category=None,
    target_distribution=None,
):
    """Scale land categories based on relative changes to food quantities.
    
    Given two food balance sheets, this model uses the relative change in
    selected items quantities to scale land categories in a land data array.

    Parameters
    ----------
    land : xarray.DataArray
        Input land array containing the land categories to be scaled.
    fbs : xarray.DataSet
        Food balance sheet dataset containing the current food quantities.
    fbs_reference : xarray.DataSet
        Food balance sheet dataset containing the reference food quantities.
    category : string, list
        Name or list of names of the land use categories to be scaled.
    items : string, list, tuple, optional
        Item or list of items to be used for scaling. If not provided, all
        items are used.
    element : string, optional
        Name of the fbs element to obtain the food quantities.
    category_dim : string, optional
        Name of the dimension along which the land use categories are defined.
        If not provided, the first non spatial dimension is used.
    keep_land_constant : bool, optional
        If True, the total land area is kept constant by scaling the other
        categories proportionally to the change in the target category. If False,
        only the target category is scaled, allowing the total land area to change.
    target_category : string, list, optional
        Name of the land category to be used as padding when keep_land_constant
        is True.
    target_distribution : array-like, xarray.DataArray, optional
        Relative distribution used to allocate land changes across target
        categories when keep_land_constant is True.
    """

    # Obtain reference and current food quantities
    if items is not None:
        items = item_parser(fbs_reference, items)
    else:
        items = fbs_reference.Item.values

    ref_quantities = fbs_reference[element].sel(Item=items).sum(dim="Item")
    obs_quantities = fbs[element].sel(Item=items).sum(dim="Item")

    # Compute scaling factor
    scaling_factor = obs_quantities / ref_quantities

    out_land = scale_land(
        land,
        origin=category,
        fraction=1 - scaling_factor,
        keep_land_constant=keep_land_constant,
        target_category=target_category,
        target_distribution=target_distribution,
        category_dim=category_dim,
    )
        
    return out_land
    