from agrifoodpy.pipeline import standalone
from agrifoodpy.impact.impact import Impact

@standalone(["dataset"], ["dataset"])
def extend_years(dataset, years, projection='empty', datablock=None):
    """
    Extends the dimensions of a dataset.
    
    Parameters
    ----------
    datablock : dict
        The datablock dictionary where the dataset is stored.
    dataset : str
        Datablock key of the dataset to extend.
    years : list
        List of years to extend the dataset to.
    projection : str
        Projection mode. If "constant", the last year of the input array
        is copied to every new year. If "empty", values are initialized and
        set to zero. If a float array is given, these are used to populate
        the new year using a scaling of the last year of the array
    """

    data = datablock[dataset].copy(deep=True)

    data = data.fbs.add_years(years, projection)

    datablock[dataset] = data 
    return dataset
