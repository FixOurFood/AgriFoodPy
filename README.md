# AgriFoodPy

AgriFoodPy is a collection of methods for manipulating and modelling agrifood
data. It provides modelling for a variety of aspects of the food system,
including food consumption paterns, environmental impact and emissions data,
population and land use. It also provides an interface to run external models by
using xarray as the data container.

In addition to this package, we have also pre-packaged some datasets for use
with agrifood. These can be found on the agrifoodpy_data repository
https://github.com/FixOurFood/agrifoodpy-data

<!-- A collection of methods for modelling agri-food and land use, including
agriculture for food and non-food uses, food production from laboratory through
horticulture to livestock to sea, and alternative land uses. It ingests current
relevant datasets, connects them to evaluate metrics, and models the impact of
agri-food system interventions on current and future metric values. -->

## Installation:

In the future, AgriFoodPy will be _pip_ installable, by running

```bash
pip install agrifoodpy
```

Currently, you install the package directly from this repository by running:

```bash
pip install git+https://github.com/FixOurFood/agrifoodpy-data.git
```

## Usage:

Each of the four basic modules on AgriFoodPy (Food, Land, Impact, Population)
has its own set of basic array manipulation functionality, a set of
modelling methods to extract basic metrics from datasets, and interfaces with
external modelling packages and code.

Agrifoodpy employs _xarray_ accesors to add additional functionality on top of
the array manipulation

Basic usage of the accesors depend on the type of array being manipulated
As an example, using the food module

```python
# import the FoodBalanceSheet accessor and FAOSTAT from agrifoodpy_data
from agrifoodpy.food import FoodBalanceSheet
from agrifoodpy_data.food import FAOSTAT

# Extract data for the UK in 2020 (Region=229, Year=2020)
food_uk = FAOSTAT.sel(Region=229, Year=2020)

# Compute the Self-sufficiency ratio using the fbs accessor SSR function
SSR = food_uk.fbs.SSR(per_item=True)

# Plot the results using the fbs accessor plot_years function
SSR.fbs.plot_years()
```

To use the specific models and interfaces to external code, these need to be
imported

```python
# import the FoodBalanceSheet accessor and FAOSTAT from agrifoodpy_data
from agrifoodpy.food import FoodBalanceSheet
from agrifoodpy_data.food import FAOSTAT
import agrifoodpy.food.model as food_model

# Extract data for the UK in 2020 (Region=229, Year=2020)
food_uk = FAOSTAT.sel(Region=229, Year=2020)

# Scale consumption of meat to 50%, 
food_uk_scaled = food_model.balanced_scaling(food_uk,
                                            items=2731,
                                            scale=0.5,
                                            constant=True)

# Plot bar summary of resultant food quantities
food_uk_scaled.fbs.plot_bars(elements=["production","imports"],
                            inverted_elements=["exports","food"])
```

In he future, we plan to implement a pipeline manager to automatize certain
aspects of the agrifood execution, and to simulate a comprehensive model where
all aspects of the food system are considered simultaneously.

## Contributing

AgriFoodPy is an open-source project which aims at improving the transparency of
evidence base food system interventions and policy making.
As such, we are happy to hear the input and ideas from the community. 

If you want to contribute, have a look at the
[discussions](https://github.com/FixOurFood/AgriFoodPy/discussions)
page or open a new [issue](https://github.com/FixOurFood/AgriFoodPy/issues)

For a comprehensive guide, please refer to the contributing guidelines to open
a pull request to contribute new functionality

