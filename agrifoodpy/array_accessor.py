import xarray as xr
import numpy as np

class XarrayAccessorBase(object):
    """Common logic for for both data structures (DataArray and Dataset).

    http://xarray.pydata.org/en/stable/internals.html#extending-xarray
    """

    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def add_items(self, items, copy_from=None):
        """Extends the item list of an input xarray object according to the
        defined input item list

        Parameters
        ----------
        items : list, int, string
            list of item names to be added to the data
        copy_from : list, int, string, optional
            If provided, this is the list of items already on the array
            to copy data from.
        
        Returns
        -------
        out : xarray.Dataset, xarray.DataArray
            Xarray object with new items added.
        """

        fbs = self._obj

        if np.isscalar(items):
            items = [items]
        
        # Check for duplicates
        indexes = np.unique(items, return_index=True)[1]
        items = [items[index] for index in sorted(indexes)] #issues with np.unique

        new_items = xr.DataArray(data = np.ones(len(items)),
                                coords = {"Item":items})

        if copy_from is not None:
            fbs_pivot = fbs.sel(Item=copy_from)
            fbs_pivot["Item"] = items
            new_fbs = fbs_pivot*new_items
            
        else:
            new_items *= np.nan
            new_fbs = fbs.isel(Item=0)*new_items
            
        # Concatenate to input array
        out = xr.concat([fbs, new_fbs], dim="Item") 
            
        return out

    def add_regions(self, regions, copy_from=None):
        """Extends the region list of an input xarray object according to the
        defined input region list

        Parameters
        ----------
        regions : list, int, string
            list of region names to be added to the data
        copy_from : list, int, string
            If provided, this is the list of regions already on the object to
            copy data from.
        labels : dict 
            Dictionary containing the new label for the regions matched to its
            corresponding label coordinate.
        
        Returns
        -------
        out : xarray.Dataset, xarray.DataArray
            Xarray object with new regions added.
        """
        
        fbs = self._obj

        if np.isscalar(regions):
            regions = [regions]

        indexes = np.unique(regions, return_index=True)[1]
        regions = [regions[index] for index in sorted(indexes)]
        
        new_regions = xr.DataArray(data = np.ones(len(regions)),
                                coords = {"Region":regions})

        if copy_from is not None:
            fbs_pivot = fbs.sel(Region=copy_from)
            fbs_pivot["Region"] = regions
            new_fbs = fbs_pivot*new_regions
            
        else:
            new_regions *= np.nan
            new_fbs = fbs.isel(Region=0)*new_regions
            
        # Concatenate to input array
        out = xr.concat([fbs, new_fbs], dim="Region") 
            
        return out
    
    def add_years(self, years, projection="empty"):
        """Extends the year range of an xarray object according to the defined
        maximum year

        Parameters
        ----------
        years : list, int
            list of years to be added to the data
        projection : string or array_like
            Projection mode. If "constant", the last year of the input array
            is copied to every new year. If "empty", values are initialized and
            set to zero. If a float array is given, these are used to populate
            the new year using a scaling of the last year of the array

        Returns
        -------
        out : xarray.Dataset, xarray.DataArray
            Xarray object with new years added.
        """

        fbs = self._obj

        if np.isscalar(years):
            years = [years]

        indexes = np.unique(years, return_index=True)[1]
        years = [years[index] for index in sorted(indexes)]
        
        if isinstance(projection, str):
            if projection == "empty":
                data = np.zeros(len(years))*np.nan
            elif projection == "constant":
                data = np.ones(len(years))
            else:
                raise ValueError("If a string, 'projection' can only be 'empty'\
                                 or 'constant'")
            
        else:
            # Should raise an exception if sizes do not match
            data = np.ones(len(years)) * projection
        
        
        new_years = xr.DataArray(data=data,
                                    coords = {"Year":years})

        # Select last year as pivot
        fbs_pivot = fbs.isel(Year=-1)
        
        # Create DS or DA by multiplying along last value
        new_fbs = fbs_pivot*new_years
        
        # Concatenate to input array
        out = xr.concat([fbs, new_fbs], dim="Year") 
            
        return out

    def group_sum(self, coordinate, new_name=None):
        """Sums quantities over items of a equal group labels and, optionally,
        renames the groups label coordinate.

        Parameters
        ----------
        fbs : xarray.Dataset
            Input xarray object
        coordinate : string
            Coordinate name to group elements and sum over 
        new_name : string, optional 
            New name for the collapsed coordinate
        

        Returns
        -------
        fbs : xarray.Dataset, xarray.DataArray
            Xarray object with new coordinate base.
        """
        
        fbs = self._obj

        grouped_fbs = fbs.groupby(coordinate).sum()

        if new_name is not None:
            grouped_fbs = grouped_fbs.rename({coordinate:new_name})

        return grouped_fbs

