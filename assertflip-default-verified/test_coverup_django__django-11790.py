from django.test import SimpleTestCase
from django.contrib.auth.forms import AuthenticationForm

class AuthenticationFormMaxLengthTest(SimpleTestCase):
    def test_username_field_maxlength_presence(self):
        """
        Test that the maxlength attribute is present in the username field's HTML.
        This confirms the expected behavior where maxlength is set.
        """
        form = AuthenticationForm()
        form_html = form.as_p()
        
        # Extract the username field's HTML
        username_field_html = form.fields['username'].widget.render('username', '')
        
        # Check that maxlength is present in the username field's HTML
        self.assertIn('maxlength', username_field_html)
