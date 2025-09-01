""" Module for impact intervention models
"""
import numpy as np


def fbs_impacts(
    fbs,
    impact_element,
    population=None,
    sum_dims=None
):
    """Computes total impacts from quantities in a food balance sheet Dataset
    or food element quantity DataArray, summing over items, regions or years if
    instructed.

    Parameters
    ----------
    fbs : xarray.DataArray or xarray.Dataset
        Food Balance Sheet array with food quantities for a set of items,
        regions and/or years.
    impact_element : xarray.DataArray
        Impact DataArray containing the impacts for set of items, regions
        and/or years.
    population : xarray.DataArray
        If given, the input impacts are considered per-capita values and
        multiplied by the population array
    sum_dims : str
        Dimension labels to sum over

    Returns
    -------
    total_impact : xarray.DataArray or xarray.Dataset
        Total impact computed from food balance sheet data and impact array
    """

    total_impact = fbs * impact_element
    if population is not None:
        total_impact *= population

    if sum_dims is not None:
        total_impact = total_impact.sum(dim=sum_dims)

    return total_impact


def fair_co2_only(emissions):
    """Simple Interface to FaIR, the Finite-amplitude Impulse-Response
    atmosferic model.

    Computes the concentration, radiative forcing and temperature anomaly for
    an array of CO2 emissions per year assuming a clean atmosphere and default
    values for amosferic parameters.

    Parameters
    ----------
    emissions : xarray.DataArray or xarray.Dataset
        Array containing GHG emissions in Gt CO2e per year

    Returns
    -------
    T : xarray.DataArray
        Temperature anomaly in Kelvin degrees at the zero layer
    C : xarray.DataArray
        Atmosferic CO2e concetration in ppm
    F : xarray.DataArray
        Effective radiative forcing in W m^-2
    """

    from fair import FAIR
    from fair.interface import fill, initialise
    f = FAIR()

    years = np.unique(emissions.Year.values)

    # Configure method, timebounds, and labels
    f.ghg_method = 'myhre1998'
    f.define_time(years[0]-0.5, years[-1]+0.5, 1)
    f.define_scenarios(["default"])
    f.define_configs(["default"])

    # Define CO2 as the only specie
    species = ['CO2']
    properties = {
        'CO2': {
            'type': 'co2',
            'input_mode': 'emissions',
            # doesn't behave as a GHG itself in the model, but as a precursor
            'greenhouse_gas': True,
            'aerosol_chemistry_from_emissions': False,
            'aerosol_chemistry_from_concentration': False,
        }}

    f.define_species(species, properties)

    # Allocate arrays
    f.allocate()

    # Set default values
    fill(f.climate_configs["ocean_heat_transfer"], [1.1, 1.6, 0.9],
         config='default')

    fill(f.climate_configs["ocean_heat_capacity"], [8, 14, 100],
         config='default')

    fill(f.climate_configs["deep_ocean_efficacy"], 1.1, config='default')

    # Set initial conditions.
    initialise(f.concentration, 278.3, specie='CO2')
    initialise(f.forcing, 0)
    initialise(f.temperature, 0)
    initialise(f.cumulative_emissions, 0)
    initialise(f.airborne_emissions, 0)

    # Fill species configs
    f.fill_species_configs()

    f.emissions.loc[{"scenario": "default",
                     "specie": "CO2",
                     "config": "default"}] = emissions.to_numpy()

    # Run and return
    f.run(progress=False)

    return_dict = {"scenario": "default", "config": "default"}

    T = f.temperature.sel(return_dict).drop_vars(
        ["scenario", "config", "layer"]).squeeze()

    C = f.concentration.sel(return_dict).drop_vars(
        ["scenario", "config", "specie"]).squeeze()

    F = f.forcing.sel(return_dict).drop_vars(
        ["scenario", "config", "specie"]).squeeze()

    return T.sel(layer=0), C, F
