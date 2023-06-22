---
title: 'AgriFoodPy: a package for modelling food systems'
tags:
  - Python
  
authors:
  - name: Juan P. Cordero
    corresponding: true
    orcid: 0000-0002-6625-7656
    affiliation: 1 # (Multiple affiliations must be quoted)

  - name: Sarah L. Bridle
    orcid: 0000-0002-0128-1006
    affiliation: 1

  - name: Kevin Donkers
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 2

  - name: Ian Harrison
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 3

  - name: Angelina Frankowska
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 4

  - name: Michelle Cain
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 4

  - name: Katherine Denby
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 1

  - name: Bob Doherty
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 1

  - name: Alana Kluczkovski
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 1

  - name: Jez Frendenburgh
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 5

  - name: Neil Ward
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 5

  - name: Ximena Schmidt
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 6

  - name: Christian Reynolds
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 7

  - name: Jacqueline Silva
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 8

  - name: Aled Jones
    orcid: XXXX-XXXX-XXXX-XXXX
    affiliation: 9

affiliations:
 - name: Department of Environment and Geography Wentworth Way, University of York, Heslington, York, YO10 5NG, UK
   index: 1
 - name:
   index: 2
 - name:
   index: 3
 - name:
   index: 4
 - name: Vice Chancellor's Office, University of East Anglia, Norwich, NR4 7TJ UK
   index: 5
 - name:
   index: 6
 - name:
   index: 7
 - name:
   index: 8
date: July 2023
bibliography: paper.bib
---

# Summary

<!-- What is the package -->
`AgriFoodPy` is an open-source Python package for interoperability of datasets,
simulation and modelling of agrifood systems.
<!-- Some specifics on how it does what it does -->
By employing xarray [@hoyer2017xarray] as the primary data structure, AgriFoodPy
provides access to a range of available agrifood data through manually formated
arrays, including geospatial, time series and tabular data from different open
sources.
The framework is region agnostic and will provide facilities to model and
simulate arbitrary data regardless of its geographic origin.

<!-- Open source development and maintenance -->
Open-source code and community development will allow a transparent view into
analysis choices and data sources, which can help provide trustworthy
evidence-based support to data-driven policy making. AgriFoodPy is developed and maintained by a diverse community of domain experts
with a focus on software sustainability and interoperability.

<!-- Current functionality -->
Version 0.1 provides access global agrifood datasets including geospatial land
use and classification data [@CEH], food supply [@FAOSTAT], life cycle assestment [@PN18] and population data[@UN].
Also included is a library of intervention models across a range of observables
and indicators, which connects with pre-existing atmospheric, land use change,
socio-economic and human health models.

<!-- Future functionality -->
Future releases will provide access to
more models and community contributed datasets formatted using xarray, as well
as implementing a pipeline manager to perform end-to-end simulations of agrifood
systems and predictions of diferent scenarios.

# Statement of need

<!-- Background and main references -->
Providing food for an ever-growing population while reducing the impact of human
activity on the environment has become one of the main current global
challenges. Local and and intergovernmental independent committees
(https://www.theccc.org.uk/) (https://www.ipcc.ch/) have reported the importance
of food production on climate change. The scenarios and projections in their
reports also highlighted the need for precise and transparent modelling of
the different aspects of the food system to help stakeholders understand the
effects of consumption patterns and farming practices.  

<!-- Current needs and requirements -->
Coordinated efforts to achieve a sustainable food system must originate from
effective policy-making based on evidence, careful choice of metrics and
indicators to describe the state of the food system, and accurate estimates of how
these metrics change under different scenarios.

<!-- Challenges and problematics -->
Existing datasets and analisys software usually rely on non standardized data
structures and predominantly closed-source code. This difficults research
and independent scrutiny of food system inverventions projections and the impact
of policy on environmental, socio-economic and health indicators.
Moreover, this forces researchers to routinely expend significant effort
replicating or re-developing existing code to reduce and analyse data.
Additionally, the opacity of some data sources and analysis choices make it
difficult to draw conclusions from equivalent comparisons between different
interventions and policy decisions.

<!-- What has been made -->
Several open initiatives exist focused on analysis and modelling of agrifood
and enviromental related data, 
Research community has also developed open-source python packages that adress
some individual aspects of modelling agrifood systems, such as geospatial
imaging (e.g. `Geopandas` [@geopandas], `Rasterio` [@rasterio]), atmospheric and
climate modelling (`Fair` [@fair]).
Other open softwares also exist in other languages, including agriculture and
farming (`APSIM` [@APSIM]), life cycle assestment (`OpenLCA`, www.openlca.org).

<!-- How does this package connect with other packages and projects -->
AgriFoodPy will provide a consistent standard for agrifood data distribution,
while also allowing external models and packages to coexist and interoperate to
allow a holistic approach to agrifood modelling.


# Acknowledgements



# References
