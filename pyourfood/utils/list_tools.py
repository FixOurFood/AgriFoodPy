import numpy as np

def tolist(item):

    itemlist = np.array(item).tolist()
    if not isinstance(itemlist, list):
        itemlist = [itemlist]

    return itemlist
