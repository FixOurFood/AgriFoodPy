---
title: 'AgriFoodPy: a package for modelling food systems'
tags:
  - Python
  
authors:
  - name: Juan P. Cordero
    corresponding: true
    orcid: 0000-0002-6625-7656
    affiliation: 1 # (Multiple affiliations must be quoted)

  - name: Kevin Donkers
    orcid: 0000-0003-0160-8467
    affiliation: 2

  - name: Ian Harrison
    orcid: 0000-0002-4437-0770
    affiliation: 3

  - name: Sarah L. Bridle
    orcid: 0000-0002-0128-1006
    affiliation: 1

  - name: Angelina Frankowska
    orcid: 0000-0003-1483-114X
    affiliation: 4

  - name: Michelle Cain
    orcid: 0000-0003-2062-6556
    affiliation: 4

  - name: Neil Ward
    orcid: 0000-0002-0732-2278
    affiliation: 5

  - name: Jez Frendenburgh
    affiliation: 5

  - name: Edward Pope
    orcid: 0000-0002-8295-2667
    affiliation: 2

  - name: Alana Kluczkovski
    orcid: 0000-0001-6462-6801
    affiliation: 6

  - name: Ximena Schmidt
    orcid: 0000-0003-0157-2679
    affiliation: 7

  - name: Jacqueline Silva
    orcid: 0000-0002-6082-8905
    affiliation: 8

  - name: Christian Reynolds
    orcid: 0000-0002-1073-7394
    affiliation: 9

  - name: Katherine Denby
    orcid: 0000-0002-7857-6814
    affiliation: 6

  - name: Bob Doherty
    orcid: 0000-0001-6724-7065
    affiliation: 10

  - name: Aled Jones
    orcid: 0000-0001-7823-9116
    affiliation: 11

affiliations:
 - name: Department of Environment and Geography Wentworth Way, University of York, Heslington, York, YO10 5NG, UK
   index: 1
 - name: Land, Environment, Economics and Policy Institute (LEEP), University of Exeter Business School, Exeter, UK
   index: 2
 - name: School of Physics and Astronomy, Cardiff University, Cardiff CF24 3AA, UK
   index: 3
 - name: Centre for Environmental and Agricultural Informatics, School of Water, Energy and Environment, Cranfield University, Cranfield MK43 0AL, UK
   index: 4
 - name: School of Environmental Sciences, University of East Anglia, Norwich, UK
   index: 5
 - name: Centre for Novel Agricultural Products (CNAP), Department of Biology, University of York, York, YO10 5DD, UK
   index: 6
 - name: Equitable Development and Resilience Research Group, College of Engineering, Design and Physical Science, Brunel University London, London, UB8 3PH, UK
   index: 7
 - name: Global Academy of Agriculture and Food Systems, The University of Edinburgh. Charnock Bradley Building, Easter Bush Campus, EH25 9RG.
   index: 8
 - name: Centre for Food Policy, City, University of London, Northampton Square, London, EC1V 0HB, UK
   index: 9
 - name: School for Business and Society, University of York
   index: 10
 - name: Global Sustainability Institute, Anglia Ruskin University, Cambridge CB1 1PT, UK
   index: 11
   
date: November 2023
bibliography: paper.bib
---

# Summary

<!-- What is this package -->
`AgriFoodPy` is an open-source Python package for processing, simulation,
and modeling of agrifood datasets and systems.
By employing `xarray` [@hoyer2017xarray] as the primary data structure, `AgriFoodPy`
provides methods to manipulate tabular data by extending `xarray` functionality
via accessor classes. It acts as an accessibility and interoperability
layer between data sources and external packages, and also bundles with a
library of models for use without any additional requirements. 

A separate repository, `agrifoodpy_data`, is actively maintained in parallel to
provide access to local and global agrifood datasets, including geospatial land
use and classification data [@CEH], food supply [@FAOSTAT], life cycle
assessment [@PN18], and population data [@UN]. The `AgriFoodPy` framework is
region-agnostic and provides facilities to model and simulate processes and
intervention impacts regardless of their geographic origin.

# Features

<!-- Current functionality -->
Version 0.1 provides table manipulation methods to extend the coordinate
dimensions of `xarray` Datasets and DataArrays, extract summary statistics, and
includes charting methods to analyze and display data.
It also includes a library of intervention models for supply and demand
changes, afforestation and agroecology, and land carbon sequestration. These can
be used to predict the effectiveness of systemic interventions through key
metrics of the food system.

<!-- External models and interoperability-->
`AgriFoodPy` provides a framework to build interfaces to external tools and
packages which can be used by the community to extend its functionality and
widen the scope of the simulated systems.
This makes it the first multipurpose tool of its kind, allowing wide analysis
of food systems data by integrating diverse datasets, models and
indicators into a unified framework. This allows researchers to make informed
decisions and identify opportunities for systemic change in all areas of food
systems, ranging from production, consumption, and land use to food security,
nutrition, health, and policy-making.

<!-- Future functionality -->
Future releases will provide access to more models and community-contributed
datasets formatted using `xarray`. Additionally, `AgriFoodPy` will implement a
pipeline manager to perform end-to-end simulations of agrifood systems, which
can be used to speed up the comparison of multiple scenarios and build easily
shareable and reproducible workflows.

<!-- Open source development and maintenance -->
Open-source code and community development will allow a transparent view into
analysis choices and data sources, which can help provide trustworthy
evidence-based support for data-driven policymaking. `AgriFoodPy` is developed and
maintained by a diverse community of domain experts with a focus on software
sustainability and interoperability.

# Statement of need

<!-- Background and main references -->
Providing food for an ever-growing population while reducing the impact of human
activity on the environment has become one of the main global challenges.
Local and intergovernmental independent committees
(https://www.theccc.org.uk/, https://www.ipcc.ch/) have reported the impact
of food production on climate change. The scenarios and projections in their
reports also highlight the need for precise and transparent modeling of
different aspects of the food system to help stakeholders understand the
effects of consumption patterns and farming practices.

<!-- Current needs and requirements -->
Coordinated efforts to achieve a sustainable food system must originate from
effective policy-making based on evidence, careful choice of metrics and
indicators to describe the state of the food system, and accurate estimates of
how these metrics change under different scenarios and decisions/interventions.

<!-- Challenges and problematics -->
Existing datasets and analysis software usually rely on non-standardized data
structures and predominantly closed-source code. This hinders research and
independent scrutiny of food system intervention projections and the impact of 
policy on environmental, socio-economic, and health indicators.
Moreover, this forces researchers to routinely expend significant effort
replicating or re-developing existing code to reduce and analyze data.
Additionally, the opacity of some data sources and analysis choices makes it
difficult to draw conclusions from equivalent comparisons between different
interventions and policy decisions.

<!-- What has been made -->
Few open initiatives exist focused on analysis and modeling of agrifood
and environmental related data, e.g., the Environmental Data Science book
(https://edsbook.org/).
The research community has developed open-source tools that address
some individual aspects of modeling agrifood systems, such as geospatial
imaging [e.g., `GeoPandas`, @geopandas; `Rasterio`, @rasterio], atmospheric
and climate modeling [`Fair`, @fair] in Python, and other open softwares in
other languages, including agriculture and farming [`APSIM`, @APSIM] and life
cycle assessment (`OpenLCA`, www.openlca.org).

<!-- How does this package connect with other packages and projects -->
`AgriFoodPy` provides a consistent standard for agrifood data distribution,
while also allowing external models and packages to coexist and interoperate,
which facilitates a holistic approach to agrifood modeling.

<!-- What projects are or will employ AgriFoodPy  -->
Plans for future use in research and communication include the FixOurFood
agrifood calculator (https://fixourfood.streamlit.app/), an interactive
modeling tool to evaluate the effect of food system transformations in the UK.
There are also plans to publish a paper on global diets their social and
environmental impacts. 

# Acknowledgements

JPC, SLB, AF, MC, KD, BD, AK and FixOurFood’s work was supported by the UKRI
Transforming Food Systems Strategic Priority Fund (grant number BB/V004581/1).
KD was funded via a doctoral training grant awarded as part of the UKRI AI
Centre for Doctoral Training in Environmental Intelligence (UKRI grant number
EP/S022074/1).
NW & JF are grateful for funding from the AFN Network+ (UKRI Agri-food for Net
Zero Network+) Grant Award EP/X011062/1
CR was funded through Transforming the UK Food System for Healthy People and a
Healthy Environment SPF Programme, Grant Award BB/V004719/1 Healthy soil,
Healthy food, Healthy people (H3).
This article has benefited from comments and suggestions of the following
people: Daniel Lewis, Joe Kennedy, Nada Saidi, Adam Amara.

# References
