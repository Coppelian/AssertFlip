import pytest
from flask.blueprints import Blueprint

def test_blueprint_empty_name():
    # Attempt to create a Blueprint with an empty name
    with pytest.raises(ValueError, match="Blueprint name must not be empty"):
        Blueprint("", __name__)
