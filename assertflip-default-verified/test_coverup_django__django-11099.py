from django.test import SimpleTestCase
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.core.exceptions import ValidationError

class UsernameValidatorTests(SimpleTestCase):
    def test_ascii_username_validator_allows_trailing_newline(self):
        validator = ASCIIUsernameValidator()
        # Username with trailing newline
        username_with_newline = "validusername\n"
        with self.assertRaises(ValidationError, msg="ASCIIUsernameValidator should not accept username with trailing newline"):
            validator(username_with_newline)

    def test_unicode_username_validator_allows_trailing_newline(self):
        validator = UnicodeUsernameValidator()
        # Username with trailing newline
        username_with_newline = "validusername\n"
        with self.assertRaises(ValidationError, msg="UnicodeUsernameValidator should not accept username with trailing newline"):
            validator(username_with_newline)
