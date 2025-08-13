import copy

def copy_datablock(datablock, key, out_key):
    """Copy a datablock element into a new key in the datablock
    
    Parameters
    ----------
    datablock : xarray.Dataset
        The datablock to print
    key : str
        The key of the datablock to print
    out_key : str
        The key of the datablock to copy to

    Returns
    -------
    datablock : dict
        Datablock to with added key
    """

    datablock[out_key] = copy.deepcopy(datablock[key])

    return datablock
