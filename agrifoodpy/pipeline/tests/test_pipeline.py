from agrifoodpy.pipeline import Pipeline, standalone

def test_init():
    pipeline = Pipeline()

def test_add_node():
    pipeline = Pipeline()
    def dummy_node(datablock, param1):
        datablock['result'] = param1
        return datablock
    
    # Test simple node addition
    pipeline.add_node(dummy_node, params={'param1': 10}, name='Test Node')
    assert(len(pipeline.nodes) == 1)
    assert(pipeline.names[0] == 'Test Node')
    assert(pipeline.params[0] == {'param1': 10})

    # Test adding node at index
    pipeline.add_node(dummy_node, params={'param1': 20}, name='Test Node 2',
                      index=0)
    assert(len(pipeline.nodes) == 2)
    assert(pipeline.names[0] == 'Test Node 2')
    assert(pipeline.params[0] == {'param1': 20})

    # Test removing a node by index
    pipeline.add_node(dummy_node, params={'param1': 30}, name='Test Node 3')
    assert(len(pipeline.nodes) == 3)
    assert(pipeline.names[2] == 'Test Node 3')
    assert(pipeline.params[2] == {'param1': 30})

    pipeline.remove_node(2)
    assert(len(pipeline.nodes) == 2)
    assert(pipeline.names[-1] == 'Test Node')
    assert(pipeline.params[-1] == {'param1': 10})

    # Test removing a node by name
    pipeline.remove_node("Test Node 2")
    assert(pipeline.names[-1] == 'Test Node')
    assert(pipeline.params[-1] == {'param1': 10})

def test_run_pipeline():
    pipeline = Pipeline()
    def node1(datablock, param1):
        datablock['result1'] = param1
        return datablock

    def node2(datablock, param2):
        datablock['result2'] = param2
        return datablock

    pipeline.add_node(node1, params={'param1': 10})
    pipeline.add_node(node2, params={'param2': 20})

    pipeline.run()
    assert(pipeline.datablock['result1'] == 10)
    assert(pipeline.datablock['result2'] == 20)

def test_run_first_node_only():
    pipeline = Pipeline()
    def node1(datablock, param1):
        datablock['result1'] = param1
        return datablock

    def node2(datablock, param2):
        datablock['result2'] = param2
        return datablock

    pipeline.add_node(node1, params={'param1': 10})
    pipeline.add_node(node2, params={'param2': 20})

    pipeline.run(to_node=1)
    assert(pipeline.datablock['result1'] == 10)
    assert('result2' not in pipeline.datablock)

def test_run_nodes_separately():
    pipeline = Pipeline()
    def node1(datablock, param1):
        datablock['result1'] = param1
        return datablock

    def node2(datablock, param2):
        datablock['result1'] *= param2
        return datablock

    pipeline.add_node(node1, params={'param1': 10})
    pipeline.add_node(node2, params={'param2': 2})

    pipeline.run(to_node=1)
    assert(pipeline.datablock['result1'] == 10)
    assert('result2' not in pipeline.datablock)

    pipeline.run(from_node=1)
    assert(pipeline.datablock['result1'] == 20)

def test_run_with_skip():
    pipeline = Pipeline()
    def node1(datablock, param1):
        datablock['result1'] = param1
        return datablock

    def node2(datablock, param2):
        datablock['result2'] = param2
        return datablock

    def node3(datablock, param3):
        datablock['result3'] = param3
        return datablock

    pipeline.add_node(node1, params={'param1': 10})
    pipeline.add_node(node2, params={'param2': 20})
    pipeline.add_node(node3, params={'param3': 30})

    pipeline.run(skip=[1])
    assert(pipeline.datablock['result1'] == 10)
    assert('result2' not in pipeline.datablock)
    assert(pipeline.datablock['result3'] == 30)

def test_standalone_decorator():
    pipeline = Pipeline()
    @standalone([], ['output1'])
    def test_func(input1, output1="output1", datablock=None):
        datablock[output1] = input1 * 2
        return datablock

    result = test_func(5)
    assert(result == 10)

    pipeline.add_node(test_func, params={'input1': 5, 'output1': 'output1'})
    pipeline.run()
    assert(pipeline.datablock['output1'] == 10)

def test_datablock_write():
    pipeline = Pipeline()
    pipeline.datablock_write(['a', 'b', 'c'], 10)
    assert(pipeline.datablock['a']['b']['c'] == 10)

    pipeline.datablock_write(['a', 'b', 'd'], 20)
    assert(pipeline.datablock['a']['b']['c'] == 10)
    assert(pipeline.datablock['a']['b']['d'] == 20)

    pipeline.datablock_write(['a', 'e'], 30)
    assert(pipeline.datablock['a']['b']['c'] == 10)
    assert(pipeline.datablock['a']['b']['d'] == 20)
    assert(pipeline.datablock['a']['e'] == 30)

    pipeline.datablock_write(['f'], 40)
    assert(pipeline.datablock['a']['b']['c'] == 10)
    assert(pipeline.datablock['a']['b']['d'] == 20)
    assert(pipeline.datablock['a']['e'] == 30)
    assert(pipeline.datablock['f'] == 40)

def test_standalone_decorator():

    from agrifoodpy.pipeline.pipeline import Pipeline, standalone

    test_datablock = {'x': 5, 'y': 10}

    # Test decorated function with single input key
    @standalone(['x'], ['out_key'])
    def double_numbers_decorated(x, out_key, datablock=None):
        datablock[out_key] = datablock[x]*2
        return datablock
    
    result_double = double_numbers_decorated(5)
    assert result_double == 10

    # Test decorated function with multiple input keys
    @standalone(['x', 'y'], ['out_key'])
    def sum_numbers_decorated(x, y, out_key, datablock=None):
        datablock[out_key] = datablock[x] + datablock[y]
        return datablock
    
    result_sum = sum_numbers_decorated(5, 10)
    assert result_sum == 15

    # Test decorated function with no input keys
    @standalone([], ['out_key'])
    def return_constant_decorated(out_key, datablock=None):
        datablock[out_key] = 42
        return datablock    
    
    result_constant = return_constant_decorated()
    assert result_constant == 42

    # Test decorated function with multiple return keys
    @standalone(['x'], ['out_key1', 'out_key2'])
    def multiple_returns_decorated(x, out_key1, out_key2, datablock=None):
        datablock[out_key1] = datablock[x] * 2
        datablock[out_key2] = datablock[x] + 10
        return datablock
    
    result_multiple = multiple_returns_decorated(5)
    assert result_multiple[0] == 10
    assert result_multiple[1] == 15

    # Test decorated function inside a pipeline
    pipeline = Pipeline(test_datablock)
    @standalone(['x'], ['out_key'])
    def pipeline_decorated(x, out_key, datablock=None):
        datablock[out_key] = datablock[x] * 3
        return datablock
    
    pipeline.add_node(pipeline_decorated, params={'x': 'x', 'out_key': 'result'})
    pipeline.run()
    assert pipeline.datablock['result'] == 15

def test_pipeline_node_decorator():

    from agrifoodpy.pipeline.pipeline import Pipeline, pipeline_node

    test_datablock_single = {'value1': 5, 'value2': 10}
    test_pipeline_single = Pipeline(test_datablock_single)

    # Test decorated function with single input key and no return key
    @pipeline_node(['x'])
    def double_numbers(x):
        return x * 2
    
    test_pipeline_single.add_node(
        double_numbers,
        params={'x': 'value1'}
        )
    
    test_pipeline_single.run()
    assert double_numbers(test_datablock_single['value1']) == 10
    assert double_numbers.__name__ in test_pipeline_single.datablock
    assert test_pipeline_single.datablock[double_numbers.__name__] == 10

    # Test decorated function with multiple input keys and no return key
    test_datablock_multiple = {'value1': 5, 'value2': 10}
    test_pipeline_multiple = Pipeline(test_datablock_multiple)

    @pipeline_node(['x', 'y'])
    def sum_numbers(x, y):
        return x + y
    
    test_pipeline_multiple.add_node(
        sum_numbers,
        params={'x': 'value1', 'y': 'value2'}
        )
    
    test_pipeline_multiple.run()
    assert sum_numbers(
        test_datablock_multiple['value1'],
        test_datablock_multiple['value2']) == 15
    assert sum_numbers.__name__ in test_pipeline_multiple.datablock
    assert test_pipeline_multiple.datablock[sum_numbers.__name__] == 15

    # Test decorated function with multiple input keys and return key
    test_datablock_with_return = {'value1': 5, 'value2': 10}
    test_pipeline_with_return = Pipeline(test_datablock_with_return)
    return_key = "result"

    @pipeline_node(['x', 'y'])
    def subtract_numbers(x, y):
        return x - y
    
    test_pipeline_with_return.add_node(
        subtract_numbers,
        params={'x': 'value1', 'y': 'value2', "return_key": return_key}
        )
    
    test_pipeline_with_return.run()
    assert subtract_numbers(
        test_datablock_with_return['value1'],
        test_datablock_with_return['value2']) == -5
    assert return_key in test_pipeline_with_return.datablock
    assert test_pipeline_with_return.datablock[return_key] == -5

    #test decorated function with external function

    test_datablock_external = {'value1': [1, 2, 3]}
    test_pipeline_external = Pipeline(test_datablock_external)

    import numpy as np

    test_pipeline_external.add_node(
        pipeline_node(input_keys=["a"])(np.mean),
        params={'a': 'value1', 'return_key': "mean_result"}
        )
    
    test_pipeline_external.run()
    assert np.mean(test_datablock_external['value1']) == 2
    assert "mean_result" in test_pipeline_external.datablock
    assert test_pipeline_external.datablock["mean_result"] == 2