from django.test import SimpleTestCase
from django.http import HttpResponse

class HttpResponseMemoryViewTest(SimpleTestCase):
    def test_memoryview_content(self):
        # Create a memoryview object
        memory_content = memoryview(b"My Content")
        
        # Initialize HttpResponse with memoryview
        response = HttpResponse(memory_content)
        
        # Access the content of the response
        content = response.content
        
        # Assert that the content is correctly represented as the original byte string
        self.assertEqual(content, b'My Content', "Content is not correctly represented as the original byte string")
