def print_datablock(
    datablock,
    key,
    attr=None,
    method=None,
    args=None,
    kwargs=None,
    preffix="",
    suffix=""
):
    """Prints a datablock element or its attributes/methods at any point in the
    pipeline execution.
    
    Parameters
    ----------
    datablock : dict
        The datablock to print from.
    key : str
        The key of the datablock to print.
    attr : str, optional
        Name of an attribute of the object to print.
    method : str, optional
        Name of a method of the object to call and print.
    args : list, optional
        Positional arguments for the method call.
    kwargs : dict, optional
        Keyword arguments for the method call.

    Returns
    -------
    datablock : dict
        Unmodified datablock to continue execution.
    """
    obj = datablock[key]

    # Extract attribute
    if attr is not None:
        if hasattr(obj, attr):
            obj = getattr(obj, attr)
        else:
            print(f"Object has no attribute '{attr}'")
            return datablock

    # Call method
    if method is not None:
        if hasattr(obj, method):
            func = getattr(obj, method)
            if callable(func):
                args = args or []
                kwargs = kwargs or {}
                try:
                    obj = func(*args, **kwargs)
                except Exception as e:
                    print(f"Error calling {method} on {key}: {e}")
                    return datablock
            else:
                print(f"'{method}' is not callable on {key}")
                return datablock
        else:
            print(f"Object has no method '{method}'")
            return datablock

    # Final print
    print(f"{preffix}{obj}{suffix}")
    return datablock