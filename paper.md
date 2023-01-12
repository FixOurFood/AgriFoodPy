---
title: 'AgriFoodPy: a package for modelling food systems'
tags:
  - Python
  - astronomy
  - dynamics
  - galactic dynamics
  - milky way
authors:
  - name: Juan P. Cordero
    corresponding: true
    orcid: 0000-0002-6625-7656
    equal-contrib: true
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Sarah L. Bridle
    orcid: 0000-0002-0128-1006
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
  - name: Angelina Frankowska
    orcid: XXXX-XXXX-XXXX-XXXX
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
  - name: Ximena Schmidt
    orcid: XXXX-XXXX-XXXX-XXXX
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
  - name: Christian Reynolds
    orcid: XXXX-XXXX-XXXX-XXXX
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
  - name: Alana Kluczkovski
    orcid: XXXX-XXXX-XXXX-XXXX
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
  - name: Jacqueline Silva
    orcid: XXXX-XXXX-XXXX-XXXX
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1

affiliations:
 - name: Department of Environment and Geography Wentworth Way, University of York, Heslington, York, YO10 5NG, UK
   index: 1
 - name: 
   index: 2
date: November 2022
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

`AgriFoodPy` is an open-source Python package for interoperability of agri-food
data, simulation and modelling of agri-food systems.
By employing xarray as the base structure, AgriFoodPy provides access to
different types of available agri-food data, including geospatial, time series
and tabular data from different open sources.

It also provides a library of models across a range of observables and
indicators, and connects with pre-existing atmospheric, land use change, socio
-economic and human health models.


# Statement of need

Providing food for an ever-growing population while reducing the impact of human
activity on the environment has become one of the main current global
challenges. Coordinated efforts must originate from effective policy-making
based on evidence, including comparisons of estimates of the effects of
interventions to the agri-food system.

We present AgriFoodPy, an open-source python package for simulating, analysing,
processing and modelling agri-food systems data, and providing access to post-
processed data products from different surveys to help predict the effect of
interventions on a range of stages of the food supply chain, including land use,
food production, processing and consumption, waste management, with an emphasis
on environmental and biodiversity impact of the food system.

Open-source code and community development will allow a transparent view into
analysis choices and data sources, which can help provide trustworthy evidence
-based support to data-driven policy making. [@PN18]

Data is stored and handled using xarray, a numpy array-like data structure which
facilitates indexing and efficiency while also allowing different types of
datasets to be used, including geo-spatial data, time series, tabular data, etc.

While still in early stages of development, AgriFoodPy implements access to
basic manipulation of these data structures and displaying routines.

# Acknowledgements

# References
