import os
import numpy as np

class UN_estimation:
    UN_estimation_file = os.path.join(os.path.dirname(__file__), 'data/Total_population_UN_median_world.txt')

    population = np.loadtxt(UN_estimation_file)
    years = np.arange(1961, 2020)

class UN_projection:

    UN_projection_file = os.path.join(os.path.dirname(__file__), 'data/Total_population_UN_median_world_projected_2020_2100.txt')

    population = np.loadtxt(UN_projection_file)
    years = np.arange(2020, 2101)
