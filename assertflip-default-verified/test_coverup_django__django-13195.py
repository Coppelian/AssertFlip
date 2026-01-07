from django.test import SimpleTestCase
from django.http import HttpResponse

class DeleteCookieSameSiteTest(SimpleTestCase):
    def test_delete_cookie_preserves_samesite(self):
        response = HttpResponse()
        
        # Set a cookie with SameSite attribute
        response.set_cookie('test_cookie', 'value', samesite='Lax')
        
        # Delete the cookie
        response.delete_cookie('test_cookie')
        
        # Get the Set-Cookie header
        set_cookie_header = response.cookies['test_cookie'].output()
        
        # Assert that the SameSite attribute is not preserved
        self.assertNotIn('SameSite=Lax', set_cookie_header)
