from agrifoodpy.pipeline.cli import main
import pytest
import os

def test_cli(tmp_path):

    # Test with no arguments
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 0

    # Argparse help
    with pytest.raises(SystemExit) as e:
        main(['--help'])
    assert e.value.code == 0

    # Process test config file
    script_dir = os.path.dirname(__file__)
    config_filename = os.path.join(script_dir, "data/empty_config.yml")   
    output_filename = str(tmp_path / 'empty.json')
    assert main([config_filename, '-o', output_filename]) == 0

    # Process test config file
    script_dir = os.path.dirname(__file__)
    config_filename = os.path.join(script_dir, "data/test_config.yml")   
    output_filename = str(tmp_path / 'test.json')
    assert main([config_filename, '-o', output_filename]) == 0
