import pytest
from unittest.mock import MagicMock
from functools import lru_cache

def test_multiple_urlresolver_instances():
    # Mock URLResolver._populate to track its calls
    mock_populate = MagicMock()

    # Simulate the _get_cached_resolver function with LRU cache
    @lru_cache(maxsize=None)
    def _get_cached_resolver(urlconf=None):
        # Simulate a URLResolver instance with a _populate method
        class MockURLResolver:
            def _populate(self):
                mock_populate()
        
        return MockURLResolver()

    # Call _get_cached_resolver with None to simulate pre-request behavior
    resolver1 = _get_cached_resolver(None)
    resolver1._populate()

    # Call _get_cached_resolver with a URL configuration to simulate post-request behavior
    resolver2 = _get_cached_resolver('myproject.urls')
    resolver2._populate()

    # Assert that URLResolver._populate is called only once
    # This is the correct behavior once the bug is fixed
    assert mock_populate.call_count == 1

