from django.test import SimpleTestCase, override_settings
from django.urls import path
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views import View

# Define the view with only an async "post" method
class Demo(View):
    """This basic view supports only POST requests"""
    async def post(self, request):
        return HttpResponse("ok")

# URL pattern to access the view
urlpatterns = [
    path("demo", Demo.as_view()),
]

@override_settings(ROOT_URLCONF=__name__)
class DemoViewTests(SimpleTestCase):
    def test_get_request_to_post_only_view(self):
        """
        Test that a GET request to a view with only an async "post" method
        results in a HttpResponseNotAllowed.
        """
        response = self.client.get('/demo')
        # Assert that the response is HttpResponseNotAllowed
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)
