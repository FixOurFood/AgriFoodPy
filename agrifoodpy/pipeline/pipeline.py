"""Pipeline implementation

This class provides methods to build and manage a pipeline for end to end
simulations using the agrifoodpy package.
"""

import copy
from functools import wraps
from inspect import signature
import time


class Pipeline():
    '''Class for constructing and running pipelines of functions with
    individual sets of parameters.'''
    def __init__(self, datablock=None):
        self.nodes = []
        self.params = []
        self.names = []
        if datablock is not None:
            self.datablock = datablock
        else:
            self.datablock = {}

    @classmethod
    def read(cls, filename):
        """Read a pipeline from a configuration file

        Parameters
        ----------
        filename : str
            The name of the configuration file.

        Returns
        -------
        pipeline : Pipeline
            The pipeline object.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def datablock_write(self, path, value):
        """Writes a single value to the datablock at the specified path.

        Parameters
        ----------
        path : list
            The datablock path to the value to be written.
        value : any
            The value to be written.
        """
        current = self.datablock

        for key in path[:-1]:
            current = current.setdefault(key, {})
        current[path[-1]] = value

    def add_node(self, node, params={}, name=None):
        """Adds a node to the pipeline, including its function and execution
        parameters.

        Parameters
        ----------
        node : function
            The function to be executed on this node.
        params : dict, optional
            The parameters to be passed to the node function.
        name : str, optional
            The name of the node. If not provided, a generic name will be
            assigned.
        """

        # Copy the parameters to avoid modifying the original dictionaries
        params = copy.deepcopy(params)

        if name is None:
            name = "Node {}".format(len(self.nodes) + 1)

        self.names.append(name)
        self.nodes.append(node)
        self.params.append(params)

    def run(self, from_node=0, to_node=None, timing=False):
        """Runs the pipeline

        Parameters
        ----------
        from_node : int, optional
            The index of the first node to be executed. Defaults to 0.

        to_node : int, optional
            The index of the last node to be executed. If not provided, all
            nodes will be executed

        timing : bool, optional
            If True, the execution time of each node will be printed. Defaults
            to False.
        """

        if to_node is None:
            to_node = len(self.nodes)

        pipeline_start_time = time.time()

        # Execute the node functions within the specified range
        for i in range(from_node, to_node):
            node = self.nodes[i]
            params = self.params[i]

            node_start_time = time.time()

            # Run node
            self.datablock = node(datablock=self.datablock, **params)

            node_end_time = time.time()
            node_time = node_end_time - node_start_time

            if timing:
                print(f"Node {i + 1}: {self.names[i]}, \
                      executed in {node_time:.4f} seconds.")

        pipeline_end_time = time.time()
        pipeline_time = pipeline_end_time - pipeline_start_time

        if timing:
            print(f"Pipeline executed in {pipeline_time:.4f} seconds.")


def standalone(input_keys, return_keys):
    """ Decorator to make a pipeline node available as a standalone function

    If datablock is not passed as a kwarg, and datasets are passed directly
    instead of datablock keys, a temporary datablock is created and the
    datasets associated with the arguments in input_keys are added to it.
    The function then returns the specified datasets in return_keys.

    Parameters
    ----------
    input_keys: list of strings
        List of dataset keys to be added to the temporary datablock
    return_keys: list of strings
        List of keys to datablock datasets to be returned by the decorated
        function.

    Returns
    -------

    wrapper: function
        The decorated function

    """
    def pipeline_decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):

            # Identify positional arguments
            func_sig = signature(test_func)
            func_params = func_sig.parameters

            kwargs.update({key: arg for key, arg in zip(func_params.keys(),
                                                        args)})

            # Make sure the datablock is passed as a kwarg, if not, create it
            datablock = kwargs.get("datablock", None)

            # Fill in missing arguments with their default values
            for key, param in func_params.items():
                if key not in kwargs:
                    # Check if there is a default value
                    if param.default is not param.empty:
                        kwargs[key] = param.default

            standalone = datablock is None
            if standalone:
                # Create datablock
                datablock = {key: kwargs[key]
                             for key in kwargs if key in input_keys}
                kwargs["datablock"] = datablock

                # Create list of keys for passed arguments only
                for key in input_keys:
                    if kwargs.get(key, None) is not None:
                        kwargs[key] = key

                # Fill return keys if they are not passed or are None
                for key in return_keys:
                    if kwargs.get(key, None) is None:
                        kwargs[key] = key

            result = test_func(**kwargs)

            # return tuple of results
            if standalone:
                if len(return_keys) == 1:
                    return result[kwargs[return_keys[0]]]
                else:
                    return tuple(result[key] for key in return_keys)

            return result
        return wrapper
    return pipeline_decorator
