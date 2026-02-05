from django.test import SimpleTestCase, RequestFactory
from django.conf import settings
from django.http import HttpResponse
from django.middleware.security import SecurityMiddleware

class SecurityMiddlewareReferrerPolicyTest(SimpleTestCase):
    def setUp(self):
        # Ensure SECURE_REFERRER_POLICY is not set to test the default behavior
        settings.SECURE_REFERRER_POLICY = None
        self.factory = RequestFactory()
        self.middleware = SecurityMiddleware()

    def test_default_referrer_policy(self):
        # Create a mock request and response
        request = self.factory.get('/')
        response = HttpResponse()

        # Process the response through the middleware
        response = self.middleware.process_response(request, response)

        # Assert that the Referrer-Policy header is set to "same-origin"
        self.assertEqual(response.get('Referrer-Policy'), 'same-origin')
