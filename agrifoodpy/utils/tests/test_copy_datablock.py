import numpy as np


def test_copy_datablock():

    from agrifoodpy.pipeline import Pipeline
    from agrifoodpy.utils.nodes import copy_datablock

    datablock = {
        'test_dataset': {
            'fbs': {
                'data': np.array([[1, 2], [3, 4]]),
                'years': [2020, 2021]
            }
        }
    }

    # Test copying the datablock
    pipeline = Pipeline(datablock=datablock)
    pipeline.add_node(
        copy_datablock,
        params={
            'key': 'test_dataset',
            'out_key': 'copied_dataset'
        },
    )

    # Execute the pipeline
    pipeline.run()

    # Check if the copied dataset exists in the datablock
    assert 'copied_dataset' in pipeline.datablock
    assert np.array_equal(
        pipeline.datablock['copied_dataset']['fbs']['data'],
        datablock['test_dataset']['fbs']['data']
    )
