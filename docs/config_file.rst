.. _config_file:

Command line tool
=================

The ``agrifoodpy`` command line tool allows you to run a pipeline of functions
defined in a configuration file. This is useful for automating workflows and
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

