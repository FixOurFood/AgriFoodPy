############
Installation
############

This page outlines how to install one of the officially distributed AgriFoodPy
releases and its dependencies, or install and test the latest development
version.

From PyPI
---------

AgriFoodPy is distributed through the  Python Package Index (PyPI_), and can be
installed using pip_:

.. code:: console

    $ pip install agrifoodpy

From GitHub
-----------

The latest development version of AgriFoodPy can be found on the main branch of
the `FixOurFood/AgriFoodPy`_ GitHub repository. This and any other branch or tag
can be installed directly from GitHub using a recent version of pip:

.. code:: console

    $ pip install agrifoodpy@git+https://github.com/FixOurFood/AgriFoodPy.git@main


.. _PyPI: https://pypi.org/project/agrifoodpy/
.. _pip: https://pip.pypa.io/
.. _FixOurFood/AgriFoodPy: https://github.com/FixOurFood/AgriFoodPy
.. _pytest: https://docs.pytest.org/

Dependencies
------------

AgriFoodPy has been tested to be compatible with Python versions 3.9 or later on
Linux, macOS and Windows operating systems. It has the following core
dependencies:

- `numpy <https://numpy.org/>`_
- `xarray <https://docs.xarray.dev/en/stable/>`_
- `matplotlib <https://matplotlib.org/>`_

Installing using pip will automatically install or update these core
dependencies if necessary.



