""" Module for impact intervention models

"""

import xarray as xr
import numpy as np

def fbs_impacts(fbs, impact_element, population=None, sum_dims=None):
    """Computes total impacts from quantities in a food balance sheet Dataset or
    food element quantity DataArray, summing over items, regions or years if
    instructed.
    """

    total_impact = fbs * impact_element
    if population is not None:
        total_impact *= population

    if sum_dims is not None:
        total_impact = total_impact.sum(dim=sum_dims)
        
    return total_impact

def fair_interface(emissions):
    """Simple Interface to FaIR, the Finite-amplitude Impulse-Response atmosferic
    model.

    Computes the concentration, radiative forcing and temperature anomaly for a 
    set of CO2 emissions assuming a clean atmosphere.
    """

    from fair import FAIR
    from fair.interface import fill, initialise
    f = FAIR()

    years = np.unique(emissions.Year.values)

    # Configure method, timebounds, and labels
    f.ghg_method='myhre1998'
    f.define_time(years[0]-0.5, years[-1], 1)
    f.define_scenarios(["afp"])
    f.define_configs(["default"])

    # Define species and their properties
    species = ['CO2']
    properties = {
        'CO2': {
            'type': 'co2',
            'input_mode': 'emissions',
            'greenhouse_gas': True,  # it doesn't behave as a GHG itself in the model, but as a precursor
            'aerosol_chemistry_from_emissions': False,
            'aerosol_chemistry_from_concentration': False,
        }}
    
    f.define_species(species, properties)

    # Allocate arrays
    f.allocate()

    # Set climate configs
    fill(f.climate_configs["ocean_heat_transfer"], [1.1, 1.6, 0.9], config='defaults')
    fill(f.climate_configs["ocean_heat_capacity"], [8, 14, 100], config='defaults')
    fill(f.climate_configs["deep_ocean_efficacy"], 1.1, config='defaults')

    # Set initial conditions
    initialise(f.concentration, 278.3, specie='CO2')
    initialise(f.forcing, 0)
    initialise(f.temperature, 0)
    initialise(f.cumulative_emissions, 0)
    initialise(f.airborne_emissions, 0)

    # Fill species configs
    f.fill_species_configs()

    f.emissions.loc[{"scenario":"afp", "specie":"CO2", "config":"default"}] = emissions
    f.run(progress=False)

    result = f[["temperature", "forcing", "concentration"]].sel(scenario="afp")

    return result
