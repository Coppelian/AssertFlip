import pytest
from requests.models import PreparedRequest
from requests.exceptions import InvalidURL

def test_invalid_url_instead_of_unicode_error():
    # The URL that triggers the bug
    malformed_url = "http://.example.com"
    
    # Prepare a request to trigger the URL preparation logic
    req = PreparedRequest()
    
    # Expect an InvalidURL exception to be raised
    with pytest.raises(InvalidURL, match="URL has an invalid label."):
        req.prepare_url(malformed_url, None)
