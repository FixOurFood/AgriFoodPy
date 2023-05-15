# AgriFoodPy food module

This directory contains data and methods for the AgriFoodPy `food` module

The `data` directory contains NetCDF xarray files containing data from different sources.
These datasets can be imported as:

```
from agrifoodpy.food.food_supply import ...
```

Currently, agrifoodpy includes the following datasets:

- `FAOSTAT`: FAO food balance sheets
- `Nutrients_FAOSTAT`: Item nutrient data derived from FAOSTAT food balance sheets
- `Nutrients`: Item nutrient data from several different sources
- `EAT_Lancet`: EAT-Lancet planetary health diet daily intakes

See the [agrifoodpy-data](https://github.com/FixOurFood/agrifoodpy-data) repository for references and more detail on how these have been generated and step-by-step guides to reproducing these files.


