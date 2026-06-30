.. _config_file:

Command line tool
=================

The ``agrifoodpy`` command line tool allows you to run a pipeline of functions
defined in a YAML configuration file. This is useful for automating workflows and
reproducibility. You can specify the configuration file and an output file for
the results.

Executing the command line tool
-------------------------------

To execute the command line tool, use the following syntax:

.. code-block:: console

    $ agrifoodpy <config_file.yml> -o <output_file.json>

The following options are available for the command line tool:

:\-o \-\-output: Specify the output file for the results. The output will be saved in JSON format.

:\-\-nodes: Print the nodes and parameters to stdout

:\-\-no-run: Do not run the pipeline

:\-\-from-node: Index of the first node to be executed

:\-\-to-node: Index of the last node to be executed

:\-\-skip-nodes: List of nodes to be skipped in the pipeline execution


Configuration files
-------------------

Configuration files are YAML files that define a pipeline of functions to be
executed by the ``agrifoodpy`` command line tool. Each function is specified
with its name and parameters, and the pipeline is executed in the order they
are defined.

.. literalinclude:: ../examples/cli/scaling_food_supply.yml
  :language: YAML
  :caption: Example of a configuration file for scaling a food balance sheet.

Each node is defined with a function to execute, and its parameters and,
optionally, a name. The function is specified in the format ``module.function``,
where ``module`` is the name of the module containing the function,
and ``function`` is the name of the function to be executed.
The parameters are specified as a dictionary of key-value pairs,
where the keys are the parameter names.

YAML constructors
-----------------

Configuration files can also use YAML tags to construct values during parsing,
which can be useful for creating complex objects without the need to read the
pipeline in a python environment and create the objects there. 

The agrifoodpy library provides access to arbitrary numpy and xarray functions
through the following YAML constructors:

* ``!numpy.<function>``
* ``!xarray.<function>``

Additionally, there are specific constructors for utility functions defined in
agrifoodpy:

* ``!scale.linear``
* ``!scale.logistic``
* ``!scale.step``
* ``!scale.pulse``
* ``!scale.smoothstep``
* ``!scale.piecewise_linear``
* ``!scale.piecewise_constant``
* ``!scale.piecewise_smoothstep``

The ``!scale`` constructors call scaling utilities from
``agrifoodpy.utils.scaling`` and return an ``xarray.DataArray``.

Example with positional arguments:

.. code-block:: yaml

  nodes:
    - function: agrifoodpy.utils.nodes.write_to_datablock
      name: Linear scale
      params:
        key: my_scale
        value: !scale.linear [2020, 2022, 2024, 2026, 1.0, 3.0]

Example with keyword arguments:

.. code-block:: yaml

  nodes:
    - function: agrifoodpy.utils.nodes.write_to_datablock
      name: Logistic scale
      params:
        key: my_scale
        value: !scale.logistic {y0: 2020, y1: 2022, y2: 2024, y3: 2026, c_init: 1.0, c_end: 3.0}

