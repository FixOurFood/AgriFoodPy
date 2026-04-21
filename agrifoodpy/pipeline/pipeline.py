"""Pipeline implementation

This class provides methods to build and manage a pipeline for end to end
simulations using the agrifoodpy package.
"""

import copy
from functools import wraps
from inspect import signature
import time
import yaml
import importlib
from ..utils.dict_utils import get_dict, set_dict

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

    @staticmethod
    def _load_function(path):
        """Load a function from a dotted path."""
        module_path, func_name = path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name)

    @classmethod
    def read(cls, filename):
        """Read a pipeline configuration from a YAML file

        Parameters
        ----------
        filename : str
            The name of the configuration file.

        Returns
        -------
        pipeline : Pipeline
            The pipeline object.
        """

        with open(filename, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        pipeline = cls()

        if config is not None:
            for step in config["nodes"]:
                func = cls._load_function(step["function"])
                params = step.get("params", {})
                name = step.get("name", func.__name__)

                pipeline.nodes.append(func)
                pipeline.params.append(params)
                pipeline.names.append(name)

        return pipeline

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

    def add_node(self, node, params={}, name=None, index=None):
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
        index : int, optional
            Index of the enw node. If None, the new node is appended at the
            end of the node list.
        """

        # Copy the parameters to avoid modifying the original dictionaries
        params = copy.deepcopy(params)

        if name is None:
            name = "Node {}".format(len(self.nodes) + 1)

        if index is None:
            index = len(self.nodes)

        self.names.insert(index, name)
        self.nodes.insert(index, node)
        self.params.insert(index, params)

    def remove_node(self, node):
        """Remove a node from the pipeline by index or name.

        Parameters
        ----------
        node : int or str
            Index of the node to remove, or its name.
        """
        # Resolve index
        if isinstance(node, int):
            index = node
            if index < 0 or index >= len(self.nodes):
                raise IndexError(f"Node index {index} out of range.")

        elif isinstance(node, str):
            matches = [i for i, name in enumerate(self.names) if name == node]
            if not matches:
                raise ValueError(f"No node found with name '{node}'.")
            if len(matches) > 1:
                raise ValueError(
                    f"Multiple nodes found with name '{node}'. "
                    "Please remove by index instead."
                )
            index = matches[0]

        else:
            raise TypeError("node must be an int (index) or str (name).")

        # Remove from all internal lists
        del self.nodes[index]
        del self.params[index]
        del self.names[index]

    def run(self, from_node=0, to_node=None, skip=None, timing=False):
        """Runs the pipeline

        Parameters
        ----------
        from_node : int, optional
            The index of the first node to be executed. Defaults to 0.

        to_node : int, optional
            The index of the last node to be executed. If not provided, all
            nodes will be executed

        skip : list of int, optional
            List of node indices to skip during execution. Defaults to None.

        timing : bool, optional
            If True, the execution time of each node will be printed. Defaults
            to False.
        """

        if to_node is None:
            to_node = len(self.nodes)

        pipeline_start_time = time.time()

        # Execute the node functions within the specified range
        for i in range(from_node, to_node):

            if skip is not None and i in skip:
                if timing:
                    print(f"Node {i + 1}: {self.names[i]}, skipped.")
                continue

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

    def print_nodes(self, show_params=True):
        """Prints the list of nodes associated with a Pipeline instance.

        Parameters
        ----------
        show_params : bool, optional
            If True, displays the parameters associated with each node.
        """

        if not self.nodes:
            print("Pipeline is empty.")
            return

        print("Pipeline nodes:")
        for i, (name, node, params) in enumerate(zip(self.names, self.nodes, self.params)):
            node_name = getattr(node, "__name__", repr(node))
            print(f"[{i}] {name}: {node_name}")
            if show_params and params:
                for k, v in params.items():
                    print(f"    {k} = {v}")


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


def pipeline_node(input_keys):
    """ Decorator to make a function compatible with pipeline execution
    
    If a datablock is passed as a kwarg, the function will be executed in
    pipeline mode, and the objects associated with the arguments in
    input_keys will be extracted from the datablock and passed to the function.
    Unregistered keyword arguments will be passed directly to the function.
    Decorated function take a "return_key" kwarg to specify the key under which
    the function output will be stored in the datablock. If not provided, the
    function name will be used as the return key.

    Parameters
    ----------
    input_keys: list of strings
        List of dataset keys to be extracted from the datablock and passed to
        the decorated function.

    Returns
    -------
    wrapper: function
        The decorated function
    """
    def pipeline_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            # Identify positional arguments
            func_sig = signature(func)
            func_params = func_sig.parameters

            kwargs.update({key: arg for key, arg in zip(func_params.keys(), args)})

            # Check whether the function is being called in a pipeline or not
            datablock = kwargs.pop("datablock", None)
            return_key = kwargs.pop("return_key", func.__name__)

            if datablock is None:
                return func(**kwargs)
            
            else:
                for key in input_keys:
                    kwargs[key] = get_dict(datablock, kwargs[key])
                result = func(**kwargs)

                set_dict(datablock, return_key, result)
                
                return datablock
        return wrapper
    return pipeline_decorator