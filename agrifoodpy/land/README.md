# AgriFoodPy land module

This directory contains data and methods for the AgriFoodPy `land` module

The `data` directory contains NetCDF xarray files containing data from different sources.
These datasets can be imported as:

```
from agrifoodpy.land.land import ...
```

Currently, agrifoodpy includes the following datasets:

- `ALC_{scale}`: Natural England Agricultural Land Classification where `{scale}` is the pixel scale in meters.
- `CEH_{scale}`: UK Centre for Ecology and Hidrology Land Cover Plus Crops where `{scale}` is the pixel scale in meters.

See the [agrifoodpy-data](https://github.com/FixOurFood/agrifoodpy-data) repository for references and more detail on how these have been generated and step-by-step guides to reproducing these files.


