import logging
import pytest

def test_caplog_clear_bug(caplog):
    def verify_consistency():
        # Assert that caplog.get_records("call") and caplog.records are the same
        assert caplog.get_records("call") == caplog.records

    # Initial consistency check
    verify_consistency()

    # Log a message
    logging.warning("test")

    # Consistency check after logging
    verify_consistency()

    # Clear the logs
    caplog.clear()

    # Consistency check after clear
    verify_consistency()
