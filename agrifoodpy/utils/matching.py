import numpy as np
import pandas as pd

def read_matching_matrix(matrix_file, skip_cols, skip_rows, delimiter=":"):

    matrix = np.genfromtxt(matrix_file, skip_header=skip_rows, delimiter=delimiter, filling_values=0)
    matrix = matrix[:, skip_cols:]
    
    return matrix
