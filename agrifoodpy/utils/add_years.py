from ..pipeline import standalone
from ..impact.impact import Impact
from ..food.food import FoodBalanceSheet
from .dict_utils import get_dict, set_dict

@standalone(["dataset"], ["dataset"])
def add_years(
    dataset,
    years,
    projection='empty',
    datablock=None
):
    """
    Extends the Year coordinates of a dataset.
    
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

    data = get_dict(datablock, dataset)

    data = data.fbs.add_years(years, projection)

    set_dict(datablock, dataset, data)

    return datablock
