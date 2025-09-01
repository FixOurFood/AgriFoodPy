def test_write_to_datablock():
    from agrifoodpy.utils.nodes import write_to_datablock

    datablock_basic = {}

    # Basic write to the datablock
    write_to_datablock(datablock_basic, "test_key", "test_value")
    assert datablock_basic["test_key"] == "test_value"

    # Write to the datablock with a tuple value
    datablock_tuple = {}
    write_to_datablock(
        datablock=datablock_tuple,
        key=("test_key_1", "test_key_2"),
        value="test_tuple_value"
        )
    assert datablock_tuple["test_key_1"]["test_key_2"] == "test_tuple_value"

    # Overwrite existing key
    datablock_overwrite = {"test_key": "old_value"}
    write_to_datablock(datablock_overwrite, "test_key", "new_value")
    assert datablock_overwrite["test_key"] == "new_value"

    # Attempt to write without overwriting an existing key
    datablock_no_overwrite = {"test_key": "existing_value"}
    try:
        write_to_datablock(
            datablock=datablock_no_overwrite,
            key="test_key",
            value="new_value",
            overwrite=False)

    except KeyError as e:
        assert str(e) == "'Key already exists in datablock and overwrite is set to False.'"