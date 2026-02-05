from django.test import SimpleTestCase
from unittest.mock import patch
from django.core.mail import EmailMessage

class EmailMessageTest(SimpleTestCase):
    def test_unicode_dns_message_id_encoding(self):
        """
        Test that when the DNS_NAME is set to a non-ASCII value and the email encoding is set to 'iso-8859-1',
        the Message-ID header is correctly encoded, ensuring the bug is fixed.
        """
        with patch("django.core.mail.message.DNS_NAME", "漢字"):
            email = EmailMessage('subject', '', 'from@example.com', ['to@example.com'])
            email.encoding = 'iso-8859-1'
            try:
                message = email.message()
                # The test should fail if the bug is present, expecting a UnicodeEncodeError.
                self.assertIn('xn--p8s937b', message['Message-ID'])
            except UnicodeEncodeError:
                self.fail("Expected Message-ID to be encoded correctly, but UnicodeEncodeError was raised.")
