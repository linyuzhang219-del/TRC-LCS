from trc_lcs.task_parser import parse_task


def test_chinese_task_parser_extracts_target_relation_and_region():
    task = parse_task("找到客厅里红色椅子旁边的包")
    assert task.target_objects == ["bag"]
    assert "red chair" in task.reference_objects
    assert "living room" in task.target_regions
    assert ("bag", "near", "red chair") in task.relations


def test_english_task_parser_runs():
    task = parse_task("find the bag near the red chair in the living room")
    assert "bag" in task.target_objects
    assert "red chair" in task.reference_objects
    assert "living room" in task.target_regions
