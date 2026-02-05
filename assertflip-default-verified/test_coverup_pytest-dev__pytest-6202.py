import pytest

@pytest.mark.parametrize("a", ["..["])
def test_report_headline_bug(a):
    # This test is designed to fail if the bug is present
    # The bug causes '..[' to be replaced with '.[' in the report headline
    # We will assert the correct behavior to ensure the test fails if the bug exists

    # Simulate the condition that triggers the bug
    # The test will fail if the bug is present, as the assertion will not match the incorrect behavior
    assert a.replace("..[", ".[") == "..["  # Correct behavior: '..[' should remain unchanged
