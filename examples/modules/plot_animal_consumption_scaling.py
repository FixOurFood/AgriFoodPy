"""
========================================
Reducing UK's animal product consumption
========================================

This example demonstrates how to combine a food supply array with a scaling
model to reduce animal product consumption.
It also employs a few functions from the ``fbs`` accessor to group and plot
food balance sheet arrays.

Consumption of animal based products is halved, while keeping total comsumed
weight constant by upscaling the consumption of vegetal products.
"""

import numpy as np

from agrifoodpy_data.food import FAOSTAT

import agrifoodpy.food
from agrifoodpy.food.model import balanced_scaling

from matplotlib import pyplot as plt

# Select food items and production values for the last year of data in the UK
# Values are in 1000 Tonnes
country_code = 229
food_uk = FAOSTAT.isel(Year=-1).sel(Region=country_code)

animal_items = food_uk.sel(Item=food_uk.Item_origin=="Animal Products").Item.values

# Scale domestic use of animal items by a factor of 0.5, while keeping
# the sum of domestic use constant. Reduce imports to account for the new
# consumption values
food_uk_scaled = balanced_scaling(food_uk,
                                  element="domestic",
                                  items=animal_items,
                                  scale=0.5,
                                  origin="-imports",
                                  fallback="-exports",
                                  constant=True)

# We group the original and scaled quantities by origin and plot to compare
food_uk_origin = food_uk.fbs.group_sum("Item_origin")
food_uk_scaled_origin = food_uk_scaled.fbs.group_sum("Item_origin")

#%%
# From the plot we can see that domestic use of animal products is reduced by
# half, while keeping total weight constant. We used ``-exports`` as the
# fallback for any extra origin required. If any item domestic use reduction
# requires more origin reduction than available, the remaining is taken from
# the ``fallback`` DataArray element.

# Plot and compare values before and after
f, axes = plt.subplots(2,1, sharex=True)
plt.subplots_adjust(hspace=0)

food_uk_origin.fbs.plot_bars(show="Item_origin",
                                  elements=["production", "imports"],
                                  inverted_elements=["exports", "domestic"],
                                  labels="show", ax=axes[0])

food_uk_scaled_origin.fbs.plot_bars(show="Item_origin",
                                  elements=["production", "imports"],
                                  inverted_elements=["exports", "domestic"],
                                  labels="show", ax=axes[1])

axes[1].set_xlabel("1000 Tonnes")
plt.tight_layout()

plt.show()