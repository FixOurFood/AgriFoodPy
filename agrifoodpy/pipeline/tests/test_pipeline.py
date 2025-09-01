from agrifoodpy.pipeline.pipeline import Pipeline, standalone

def test_init():
    pipeline = Pipeline()

def test_add_node():
    pipeline = Pipeline()
    def dummy_node(datablock, param1):
        datablock['result'] = param1
        return datablock

    pipeline.add_node(dummy_node, params={'param1': 10}, name='Test Node')
    assert(len(pipeline.nodes) == 1)
    assert(pipeline.names[0] == 'Test Node')
    assert(pipeline.params[0] == {'param1': 10})

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