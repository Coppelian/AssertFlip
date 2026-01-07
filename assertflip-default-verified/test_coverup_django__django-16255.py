from django.test import SimpleTestCase
from django.contrib.sitemaps import Sitemap

class MockSitemap(Sitemap):
    def items(self):
        # Return an empty list to simulate a sitemap with no items
        return []

    def lastmod(self, item):
        # Callable lastmod method
        return None

class SitemapTests(SimpleTestCase):
    def test_get_latest_lastmod_with_no_items(self):
        """
        Test that get_latest_lastmod returns None when items list is empty.
        """
        sitemap = MockSitemap()
        result = sitemap.get_latest_lastmod()
        self.assertIsNone(result, "Expected None when no items are present, but got a different result.")
