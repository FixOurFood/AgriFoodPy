"""
==============================================
Reforest half of UK's ALC 4 and 5 pasture land 
==============================================

This example demonstrates how to combine different land data arrays using the
``land`` accessor and how to use the carbon sequestration model to compute
additional carbon sequestration from reforested land.

Two datasets are imported from the agrifoodpy_data package

- ALC: Agricultural Land Classification data, which assigns a grade to UK's land in terms of its suitability for agricultural use.
- LC: CEH UK Land Classification map, which indicates the type of land use and assigns and value to the dominant use on each pixel

Both have the same pixel scale and are defined over the same spatial grid.

"""


import numpy as np
import xarray as xr

from agrifoodpy_data.land import UKCEH_LC_1000 as LC, ALC_1000 as ALC

from agrifoodpy.land.land import LandDataArray
from agrifoodpy.land.model import land_sequestration

from agrifoodpy.food.food import FoodElementSheet

from matplotlib import pyplot as plt

land_use = LC.copy(deep=True)
land_use = land_use["dominant_aggregate"]

f, axes = plt.subplots(1, 2, sharey=True)
plt.subplots_adjust(wspace=0)

land_use.land.plot(ax=axes[0])
ALC.land.plot(ax=axes[1])
plt.show()

#%%
# We obtain the total area of land being used for pasture on low
# grade agricultural land. Pasture identifier is 1
# Then we use the carbon sequestration model to reforest half of this fraction

# Align the two land maps to compute overlap areas
ALC, land_use = xr.align(ALC, land_use)
total_area_england = ALC.land.area_by_type().sum()

pasture_4_5 = land_use.land.area_overlap(ALC, values_left=1,
                                         values_right=[4,5]).sum()

# Maximum sequestration [t CO2e / yr]
broadleaf_max_seq = 5.7
coniferous_max_seq = 14
broadleaf_fraction = 0.5

seq_forest= broadleaf_max_seq * (broadleaf_fraction) + \
                     coniferous_max_seq * (1-broadleaf_fraction)

co2e_seq = land_sequestration(land_use, [1,2], max_seq=seq_forest,
                     fraction=[0.0, pasture_4_5/total_area_england*0.5],
                     years = np.arange(2020,2070),
                     growth_timescale=25)

ax = co2e_seq.fes.plot_years()
ax.set_ylabel("[t CO2 / yr]")
ax.set_xlabel("Year")
plt.show()
