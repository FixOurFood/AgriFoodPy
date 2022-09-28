# AgriFoodPy
A collection of methods for modelling agri-food and land use, including agriculture for food and non-food uses, food production from laboratory through horticulture to livestock to sea, and alternative land uses. It ingests current relevant datasets, connects them to evaluate metrics, and models the impact of agri-food system interventions on current and future metric values.

## Installation:

- clone the repository
```
git clone https://github.com/FixOurFood/AgriFoodPy.git
```

- use conda to create an environment called AgriFoodPy and install the packages listed in the environment.yml file
```
cd AgriFoodPy
conda env create -f environment.yml
```

- Create a conda environment
```
conda activate agrifoodpy
```

- Set up AgriFoodPy (so any changes to the code are implemented immediately)
```
python setup.py develop
```

- Or if you don't want to use conda you can use pip instead by typing 
```
python setup.py install
```

- Start interacting with AgriFoodPy through a Jupyter notebook:
```
jupyter notebook
```
- Go to notebooks/examples and run a demo!
