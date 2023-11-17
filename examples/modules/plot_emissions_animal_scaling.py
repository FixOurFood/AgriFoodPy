"""
===================================================
Plot emissions from different item groups and years
===================================================

This example demonstrates how manipulate a Food Balance Sheet array, add
items and years to it and combine it with impact data to plot total GHG
emissions dissagregated by selected coordinates. 

Two datasets are imported from the agrifoodpy_data package:

- FAOSTAT: United Nations Food and Agriculture Organization Food Balance Sheets
- PN18: Poore & Nemecek (2018) LCA data, scaled to match the FAOSTAT item base
"""

import numpy as np
import xarray as xr

from agrifoodpy_data.impact import PN18_FAOSTAT as PN18
from agrifoodpy_data.food import FAOSTAT

import agrifoodpy.food
from agrifoodpy.impact.model import fbs_impacts

from matplotlib import pyplot as plt

# Load FAOSTAT array to memory.
FAOSTAT.load();

# Select food items and production values for the UK and the US
# Values are in [1000 Tonnes]
country_codes = [229, 231]
food = FAOSTAT.sel(Region=country_codes)["production"]

# Convert emissions from [g CO2e] to [Gt CO2e]
ghg_emissions = PN18["GHG Emissions"] / 1e6
food_emissions = fbs_impacts(food, ghg_emissions)

ax = food_emissions.fbs.plot_years(show="Region", labels=["UK", "USA"])
ax.set_xlabel("Year")
ax.set_ylabel("GHG emissions Gt CO2e")

plt.show()

#%%
# We can also plot by item origin by using the group_sum accessor function
food_emissions_origin = food_emissions.fbs.group_sum("Item_origin")
ax = food_emissions_origin.fbs.plot_years(show="Item_origin", labels="show")
ax.set_xlabel("Year")
ax.set_ylabel("GHG emissions [Gt CO2e]")
plt.show()

#%%
# We can add an item to the emissions DataArray and a new list of years,
# scaling the values linearly

emissions_proj = food_emissions.fbs.add_items(items=5000)
emissions_proj.loc[{"Item":5000}] = 2*food_emissions.sel(Item=2731)

proj = np.linspace(1, 1.5, num=10)
emissions_proj = emissions_proj.fbs.add_years(years=np.arange(2021,2031), projection="constant")
emissions_proj.loc[{"Year":np.arange(2021,2031)}] *= xr.DataArray(np.linspace(1, 1.1, num=10), coords={"Year":np.arange(2021,2031)})
emissions_by_origin_proj = emissions_proj.fbs.group_sum("Item_origin")
ax = emissions_by_origin_proj.fbs.plot_years(show="Item_origin", labels="show")

ax.set_xlabel("Year")
ax.set_ylabel("GHG emissions [Gt CO2e]")
ax.axvline(2020, linewidth=0.5, alpha=0.5, color="k")

plt.show()