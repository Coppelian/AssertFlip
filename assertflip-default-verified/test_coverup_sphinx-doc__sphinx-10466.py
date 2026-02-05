import pytest
from sphinx.builders.gettext import Message

def test_message_locations_duplicates():
    # Simulate input with duplicate locations
    text = "Sample text"
    locations = [
        ("../../manual/modeling/hair.rst", 0),
        ("../../manual/modeling/hair.rst", 0),  # Duplicate
        ("../../manual/modeling/hair.rst", 0),  # Duplicate
        ("../../manual/physics/dynamic_paint/brush.rst", 0),
        ("../../manual/physics/dynamic_paint/brush.rst", 0)  # Duplicate
    ]
    uuids = ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]

    # Create a Message object
    message = Message(text, locations, uuids)

    # Check for duplicates in the locations list
    assert len(message.locations) == len(set(message.locations)), "BUG: locations list contains duplicates"

    # Cleanup: No state pollution as we are not modifying any global state

