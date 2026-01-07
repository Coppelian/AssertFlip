import pytest
import requests

def test_put_request_with_binary_payload():
    # Setup: Define the URL and the binary payload
    url = "http://httpbin.org/put"
    binary_payload = u"ööö".encode("utf-8")

    # Action: Send a PUT request with the binary payload
    # We expect this to succeed without raising an exception
    response = requests.put(url, data=binary_payload)

    # Assert: Check that the request was successful
    assert response.status_code == 200
