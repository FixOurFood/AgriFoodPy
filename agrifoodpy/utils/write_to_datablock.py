from .dict_utils import set_dict

def write_to_datablock(datablock, key, value, overwrite=True):
    """Writes a value to a specified key in the datablock.

    Parameters
    ----------
    datablock : dict
        The datablock to write to.
    key : str
        The key in the datablock where the value will be written.
    value : any
        The value to write to the datablock.
    overwrite : bool, optional
        If True, overwrite the existing value at the key.
        If False, do not overwrite.

    Returns
    -------
    datablock : dict
        The updated datablock with the new key-value pair.
    """
    
    if not overwrite and key in datablock:
        raise KeyError(f"Key already exists in datablock and overwrite is set to False.")
    
    set_dict(datablock, key, value)
    
    return datablock