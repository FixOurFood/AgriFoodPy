""" Module for land intervention models

"""

import xarray as xr
import numpy as np
from agrifoodpy.land.land import LandDataArray
from agrifoodpy.utils import scaling

def carbon_sequestration(land_da, categories,
                         f_forest=0,
                         f_agroforestry=0,
                         f_silvopasture=0,
                         f_broadleaf=0.5,
                         max_seq_broadleaf=5.7,
                         max_seq_coniferous=14,
                         max_seq_agroforestry=1.473,
                         max_seq_silvopasture=6.26,
                         years=None,
                         growth_timescale=15):
    """Additional sequestration model.
    
    Computes the anual additional sequestration from land use change as a
    function of the fraction of arable and pasture land to be converted into
    forest, agroforestry and silvopasture land. 
    
    Given a map with either percentages per pixel or pixel absolute values for
    arable and pasture land it computes the yearly additional sequestration
    from the land use change.

    Parameters
    ----------
    land : xarray.Dataset or xarray.Dataarray
        Input land array containing arable and pasture land values per pixel.
        If a dataarray, the values of the array should contain the index of the
        dominant category at each position. If a dataset, each dataarray should
        contain the percentage of each position corresponding to category.
    categories : int, array
        Identifiers of the land categories to be converted. The agroforestry,
        forest and silvopasture array lenghts must match the lenght of this
        array.
    forest_fraction : float, array
        Fraction of each land category converted to forest 
    agroforestry_fraction : float, array
        Fraction of each land category converted to agroforestry 
    silvopasture_fraction : float, array
        Fraction of each land category converted to silvopasture 
    broadleaf_ratio : float
        Relative fraction of broadleaf species used for forestation. Remaining
        percentage is assumed to be coniferous
    max_seq_broadleaf : float
        Fully grown broadleaf forest carbon sequestration expressed in
        [t CO2e / ha / year]
    max_seq_coniferous : float
        Fully grown coniferous forest carbon sequestration expressed in
        [t CO2e / ha / year]
    max_seq_agroforestry : float
        Fully grown agroforestry land carbon sequestration expressed in
        [t CO2e / ha / year]
    max_seq_silvopasture : float
        Fully grown silvopasture land carbon sequestration expressed in
        [t CO2e / ha / year]    
    years : int, array
        Year range length, or array of years for which the sequestratio is
        computed. If not given, stationary maximum values are returned 
    growth_timescale : float
        Time in years for land to reach full sequestration potential


    Returns
    -------
    seq : xarray.Dataset
        Dataset with the per year sequestration from each component
    """
    
    f_forest = np.array(f_forest)
    f_agroforestry = np.array(f_agroforestry)
    f_silvopasture = np.array(f_silvopasture)
    
    # Check all fractions are between 0 and 1     
    for arr in [f_forest, f_agroforestry, f_silvopasture]:
        if not (0 <= arr).all() and (arr <= 1).all():
            raise ValueError("Input fraction values must be between 0 and 1")
            
    # Check all fractions add up to less than 1
    for i in range(len(categories)):
        if f_forest[i] + f_agroforestry[i] + f_silvopasture[i] > 1:
            raise ValueError("Total fraction change for each category must be \
                             less or equal than 1")
    
    pixel_count_category = land_da.land.area_by_type(values=categories)
    # area in hectares
    area_category = pixel_count_category * 100
    
    if years is not None:
        # and then the sequestration as a function of time    
        y0 = 0
        y1 = 0
        y2 = growth_timescale
        y3 = years
        scale = scaling.linear_scale(y0, y1, y2, y3, 0, 1)
    else:
        scale = 1
    
    # afforestation
    seq_forest = max_seq_broadleaf * (f_broadleaf) + \
                     max_seq_coniferous * (1-f_broadleaf)
    
    forest_area = area_category * f_forest
    total_seq_forest = forest_area.sum() * scale * seq_forest
    
    # agroforestry    
    agroforestry_area = area_category * f_agroforestry
    total_seq_agroforestry = agroforestry_area.sum() * scale * \
        max_seq_agroforestry
        
    # silvopasture    
    silvopasture_area = area_category * f_silvopasture
    total_seq_silvopasture = silvopasture_area.sum() * scale * \
        max_seq_silvopasture
    
    sequestration_dataset = xr.Dataset({
        "afforestation" : total_seq_forest,
        "agroforestry" : total_seq_agroforestry,
        "silvopasture" : total_seq_silvopasture
    })
    
    return sequestration_dataset

def production_from_land():
    """Food balance sheet from land use.

    Generates a production sheet dataarray from a land dataarray or dataset
    describing the land use at any given position and, optionally, a map
    describing yield per position.



    """