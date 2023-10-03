"""Population module.
"""

import numpy as np
import xarray as xr

def population(years, regions, quantities, datasets=None, long_format=True):
    """Population style dataset constructor

    Parameters
    ----------
    years : (ny,) array_like
        The year values for which coordinates will be created.
    regions : (nr,) array_like, optional
        The region identifying ID or strings for which coordinates will be
        created.
    quantities : ([nd], ny, nr) ndarray
        Array containing the population for each combination of `Year` and
        `Region`.
    datasets : (nd,) array_like, optional
        Array with model name strings. If provided, a dataset is created
        for each element in `datasets` with the quantities being each of the
        sub-arrays indexed by the last coordinate of the input array.
    long_format : bool
        Boolean flag to interpret data in long or wide format

    Returns
    -------
    data : xarray.Dataset
        Population dataset containing the population for each `Year` and
        `Region` with one dataarray per element in `dataset`.
    """

    # if the input has a single element, proceed with long format
    if np.isscalar(quantities):
        long_format = True

    quantities = np.array(quantities)

    # Identify unique values in coordinates
    _years = np.unique(years)
    _regions = np.unique(regions)
    coords = {"Year" : _years,
              "Region" : _regions}

    # find positions in output array to organize data
    ii = [np.searchsorted(_years, years), np.searchsorted(_regions, regions)]
    size = (len(_years), len(_regions))

    # Create empty dataset
    data = xr.Dataset(coords = coords)

    if long_format:
        # dataset, quantities
        ndims = 2
    else:
        # dataset, year, region
        ndims = 3

    # make sure the long format has the right number of dimensions
    while len(quantities.shape) < ndims:
        quantities = np.expand_dims(quantities, axis=0)

    # If no dataset names are given, then create generic ones, one for each
    # dataset
    if datasets is None:
        datasets = [f"Population {id}" for id in range(quantities.shape[0])]

    # Else, if a single string is given, transform to list. If doesn't match
    # the number of datasets created above, xarray will return an error.
    elif isinstance(datasets, str):
        datasets = [datasets]

    if long_format:
        # Create a datasets, one at a time
        for id, dataset in enumerate(datasets):
            values = np.zeros(size)*np.nan
            values[tuple(ii)] = quantities[id]
            data[dataset] = (coords, values)

    else:
        quantities = quantities[:, ii[0]]
        if len(quantities.shape) < ndims:
            quantities = np.expand_dims(quantities, axis=0)

        quantities = quantities[..., ii[1]]
        if len(quantities.shape) < ndims:
            quantities = np.expand_dims(quantities, axis=0)
        # Create a datasets, one at a time
        for id, dataset in enumerate(datasets):
            values = quantities[id]
            data[dataset] = (coords, values)

    return data

@xr.register_dataarray_accessor("pop")
class PopulationDataArray:
    def __init__(self, xarray_obj):
        self._validate(xarray_obj)
        self._obj = xarray_obj

    @staticmethod
    def _validate(obj):
        """Validate pop xarray, checking it is a DataSet or DataArray
        """
        if not isinstance(obj, xr.Dataset):

            raise TypeError("Population array must be an xarray.DataSet")
        
    def add_years(self, years, projection="empty"):
        """Extends the year range of a population array according to the
        defined maximum year

        Parameters
        ----------
        pop : xarray.Dataset
            Input population Dataset
        years : list, int
            list of years to be added to the data
        projection : string or array_like
            Projection mode. If "constant", the last year of the input
            population array is copied to every new year. If "empty", values are
            initialized and set to zero. If a float array is given, these are
            used to populate the new year using a scaling of the last year of
            the array

        Returns
        -------
        pop : xarray.Dataset
            Population dataset with new years added.
        """

        pop = self._obj

        indexes = np.unique(years, return_index=True)[1]
        years = [years[index] for index in sorted(indexes)]
        
        if projection == "empty":
            data = np.zeros(len(years))*np.nan
        elif projection == "constant":
            data = np.ones(len(years))
        else:
            data = np.ones(len(years)) * projection
        
        new_years = xr.DataArray(data=data,
                                    coords = {"Year":years})

        # Select last year as pivot
        pop_pivot = pop.isel(Year=-1)
        
        # Create DS or DA by multiplying along last value
        new_pop = pop_pivot*new_years
        
        # Concatenate to input array
        concat_pop = xr.concat([pop, new_pop], dim="Year") 
            
        return concat_pop
    
    def add_regions(self, regions, copy_from=None):
        """Extends the region list of a population array according to the
        defined input region list

        Parameters
        ----------
        pop : xarray.Dataset
            Input population Dataset
        new_regions : list, int, string
            list of region names to be added to the data
        copy_from : list, int, string
            If provided, this is the list of regions already on the population
            array to copy data from.
        labels : dict 
            Dictionary containing the new label for the regions matched to its
            corresponding label coordinate.
        
        Returns
        -------
        pop : xarray.Dataset
            population dataset with new regions added.
        """
        
        pop = self._obj

        indexes = np.unique(regions, return_index=True)[1]
        regions = [regions[index] for index in sorted(indexes)]
        
        new_regions = xr.DataArray(data = np.ones(len(regions)),
                                coords = {"Region":regions})

        if copy_from is not None:
            pop_pivot = pop.sel(Region=copy_from)
            pop_pivot["Region"] = regions
            new_pop = pop_pivot*new_regions
            
        else:
            new_regions *= np.nan
            new_pop = pop.isel(Region=0)*new_regions
            
        # Concatenate to input array
        concat_pop = xr.concat([pop, new_pop], dim="Region") 
            
        return concat_pop
    
    def group_sum(self, coordinate, new_name=None):
        """Sums quantities over equally labeled elements and, optionally,
        renames the groups label coordinate.

        Parameters
        ----------
        pop : xarray.Dataset
            Input population Dataset
        coordinate : string
            Coordinate name to group elements and sum over them 
        new_name : string, optional 
            New name for the collapsed coordinate
        
        Returns
        -------
        pop : xarray.Dataset
            Population dataset with new coordinate base.
        """
        
        pop = self._obj

        grouped_pop = pop.groupby(coordinate).sum()

        if new_name is not None:
            grouped_pop = grouped_pop.rename({coordinate:new_name})

        return grouped_pop
