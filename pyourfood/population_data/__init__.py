import os
import numpy as np

class UN_population:
    UN_estimation_file = os.path.join(os.path.dirname(__file__), 'data/Total_population_UN_median_world_projected_2020_2100.txt')
    UN_projection_file = os.path.join(os.path.dirname(__file__), 'data/Total_population_UN_median_world_projected_2020_2100.txt')

    estimation = np.loadtxt(UN_estimation_file)
    projection = np.loadtxt(UN_projection_file)

    years_estimation = np.arange(1961, 2020)
    years_projection = np.arange(2020, 2100)
