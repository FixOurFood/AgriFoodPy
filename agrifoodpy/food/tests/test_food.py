import numpy as np
import pytest

def test_constructor_long():
    from agrifoodpy.food.food_supply import FoodSupply
    """ Test food supply constructor with toy data in long input format"""

    items = ["chicken", "chicken", "chicken", "beef"]
    years = np.array([1990, 1991, 1992, 1992])
    regions = ["UK", "UK", "UK", "USA"]
    quantity = np.arange(4)
    elements = ["Food", "Waste"]

    # Single item, single year
    FoodSupply(items=items[0],
               years=years[0],
               quantities=quantity[0])

    # Single item, single year, single region
    FoodSupply(items=items[0],
               years=years[0],
               regions=regions[0],
               quantities=quantity[0])

    # Single item, single year, single region, named element
    FoodSupply(items=items[0],
               years=years[0],
               regions=regions[0],
               quantities=quantity[0],
               elements=elements[0])

    # Single item, many years, single region
    FoodSupply(items=items[:3],
               years=years[:3],
               regions=regions[:3],
               quantities=quantity[:3])

    # Many items, many years, many regions
    FoodSupply(items=items,
               years=years,
               regions=regions,
               quantities=quantity)

    # Many items, many years, many regions, multiple named elements
    FoodSupply(items=items,
               years=years,
               regions=regions,
               quantities=[quantity, 0.3*quantity],
               elements=elements)
    
def test_constructor_wide():

    from agrifoodpy.food.food_supply import FoodSupply
    """ Test food supply constructor with toy data in wide input format"""

    items = ["chicken", "beef"]
    years = np.array([1990, 1991, 1992])
    regions = ["UK", "USA"]
    elements = ["Food", "Waste"]

    quantity = 100 + 10*np.arange(len(elements) * len(items) * len(years) * len(regions))
    quantity = quantity.reshape(len(elements), len(items), len(years), len(regions))

    # Single item, single year
    FoodSupply(items=items[0],
               years=years[0],
               quantities=quantity[0,0,0,0],
               long_format=False)

    # Single item, single year, single region
    FoodSupply(items=items[0],
               years=years[0],
               regions=regions[0],
               quantities=quantity[0,0,0,0],
               long_format=False)

    # Single item, single year, single region, named element
    FoodSupply(items=items[0],
               years=years[0],
               regions=regions[0],
               quantities=quantity[0,0,0,0],
               elements=elements[0],
               long_format=False)

    # Single item, many years, single region
    FoodSupply(items=items[0],
               years=years,
               regions=regions[0],
               quantities=quantity[0,0,:,0],
               long_format=False)

    # Many items, many years, many regions
    FoodSupply(items=items,
               years=years,
               regions=regions,
               quantities=quantity,
               long_format=False)

    # Many items, many years, many regions, multiple named elements
    FoodSupply(items=items,
               years=years,
               regions=regions,
               quantities=quantity,
               elements=elements,
               long_format=False)

    

def test_scale_add():
    pass

def test_scale_food():
    pass
