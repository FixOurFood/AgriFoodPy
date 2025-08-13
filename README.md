# AgriFoodPy

[![Documentation Status](https://readthedocs.org/projects/agrifoodpy/badge/?version=latest)](https://agrifoodpy.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/FixOurFood/AgriFoodPy/actions/workflows/test-conda.yml/badge.svg)](https://github.com/FixOurFood/AgriFoodPy/actions/workflows/test-conda.yml)

AgriFoodPy is a collection of methods for manipulating and modelling agrifood
data. It provides modelling for a variety of aspects of the food system,
including food consumption paterns, environmental impact and emissions data,
population and land use. It also provides an interface to run external models by
using xarray as the data container.

AgriFoodPy also provides a pipeline manager to build end-to-end simulations and
analysis toolchains. Modules can also be executed in standalone mode, which
does not require a pipeline to be defined.

In addition to this package, we have also pre-packaged some datasets for use
with agrifood. These can be found on the agrifoodpy_data repository
https://github.com/FixOurFood/agrifoodpy-data

<!-- A collection of methods for modelling agri-food and land use, including
agriculture for food and non-food uses, food production from laboratory through
horticulture to livestock to sea, and alternative land uses. It ingests current
relevant datasets, connects them to evaluate metrics, and models the impact of
agri-food system interventions on current and future metric values. -->

## Installation:

AgriFoodPy can be installed using _pip_, by running

```bash
pip install agrifoodpy
```

UK data to test the package is available from the agrifoodpy_data repository
which currently can be installed using

```bash
pip install git+https://github.com/FixOurFood/agrifoodpy-data.git@importable
```

## Usage:

AgriFoodPy modules can be used to manipulate food system data in standalone mode
or by constructing a pipeline of modules which can be executed partially or
completely. 


To build a pipeline
```python
from agrifoodpy.pipeline import Pipeline
from agrifoodpy.utils.load_dataset import load_dataset
from agrifoodpy.food.model import 
import matplotlib.pyplot as plt

# Create pipeline object
fs = Pipeline()

# Add node to load food balance sheet data from external module.
fs.add_node(load_dataset,
            {
                "datablock_path": "food",
                "module": "agrifoodpy_data.food",
                "data_attr": "FAOSTAT",
                "coords": {"Year":np.arange(1990, 2010), "Region":229}
            })


# Add node convert scale Food Balance Sheet by a constant
fs.add_node(fbs_convert,
            {
                "fbs":"food",
                "convertion_arr":1e-6 # From 1000 Tonnes to kg
            })

fs.run()

results = fs.datablock
```

## Examples and documentation

[Examples](https://agrifoodpy.readthedocs.io/en/latest/examples/index.html)
demonstrating the functionality of AgriFoodPy can be the found in the
[package documentation](https://agrifoodpy.readthedocs.io/en/latest/).
These include the use of accessors to manipulate data and access to basic
models.

## Contributing

AgriFoodPy is an open-source project which aims at improving the transparency of
evidence base food system interventions and policy making.
As such, we are happy to hear the input and ideas from the community. 

If you want to contribute, have a look at the
[discussions](https://github.com/FixOurFood/AgriFoodPy/discussions)
page or open a new [issue](https://github.com/FixOurFood/AgriFoodPy/issues)

For a comprehensive guide, please refer to the contributing guidelines to open
a pull request to contribute new functionality

