import pytest
from requests import Session
from requests.models import Request, PreparedRequest

def test_get_request_does_not_include_content_length_header(monkeypatch):
    # Mock the adapter's send method to capture the prepared request
    class MockAdapter:
        def send(self, request, **kwargs):
            # Assert that the 'Content-Length' header is NOT present, which is the correct behavior
            assert 'Content-Length' not in request.headers
            # Return a mock response object
            class MockResponse:
                status_code = 503  # Simulate the server returning a 503 error due to 'Content-Length'
                headers = request.headers
                cookies = {}
            return MockResponse()

    # Mock the get_adapter method to return the mock adapter
    def mock_get_adapter(self, url):
        return MockAdapter()

    # Use monkeypatch to replace the get_adapter method with the mock_get_adapter
    monkeypatch.setattr(Session, 'get_adapter', mock_get_adapter)

    # Create a session and send a GET request
    session = Session()
    response = session.get('http://example.com')

    # Assert that the response status code is 503, indicating the server rejected the request due to 'Content-Length'
    assert response.status_code == 503

    # Assert that 'Content-Length' is NOT present in the headers, which is the correct behavior
    assert 'Content-Length' not in response.headers

