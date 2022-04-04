from pyourfood.food_data import FAOSTAT
from pyourfood.population_data import UN_population
import pyourfood
import numpy as np

data = FAOSTAT.data
pop = UN_population.estimation

items = [2511, 2513] #yes
years = [1999, 2001]
# items = np.array([2511, 2513]) #yes
# items = 2511 #no
# items = [2511] #yes

print(pop)

print(pyourfood.food.extract_item(data, items))
print(pyourfood.food.food_supply(data, item=items, year=years))
print(pyourfood.food.protein_supply_quantity(data, item=items, year=years))
