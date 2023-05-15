# AgriFoodPy impact module

This directory contains data and methods for the AgriFoodPy `impact` module

The `data` directory contains NetCDF xarray files containing data from different sources.
These datasets can be imported as:

```
from agrifoodpy.impact.impact import ...
```

Currently, agrifoodpy includes the following datasets:

- `PN18`: Poore & Nemecek (2018) LCA impact data
- `PN18_FAOSTAT`: FAOSTAT item base refactorisation of Poore & Nemecek (2018) LCA impact data

See the [agrifoodpy-data](https://github.com/FixOurFood/agrifoodpy-data) repository for references and more detail on how these have been generated and step-by-step guides to reproducing these files.


