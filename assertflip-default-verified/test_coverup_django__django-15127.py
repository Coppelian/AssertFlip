from django.test import SimpleTestCase, override_settings
from django.contrib.messages.storage.base import Message

class MessageLevelTagOverrideTests(SimpleTestCase):
    @override_settings(MESSAGE_TAGS={50: 'custom_tag'})
    def test_level_tag_with_override_settings(self):
        """
        Test that the level_tag property updates with @override_settings.
        """
        # Create a Message instance with a level that should map to the overridden tag
        message = Message(level=50, message="Test message")

        # Assert that the level_tag is 'custom_tag', indicating the bug is fixed
        self.assertEqual(message.level_tag, 'custom_tag')
