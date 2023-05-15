# AgriFoodPy population module

This directory contains data and methods for the AgriFoodPy `population` module

The `data` directory contains NetCDF xarray files containing data from different sources.
These datasets can be imported as:

```
from agrifoodpy.population.population import ...
```

Currently, agrifoodpy includes the following datasets:

- `UN`: United Nations population estimations and projections.

See the [agrifoodpy-data](https://github.com/FixOurFood/agrifoodpy-data) repository for references and more detail on how these have been generated and step-by-step guides to reproducing these files.


