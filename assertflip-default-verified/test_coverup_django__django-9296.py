from django.test import SimpleTestCase
from django.core.paginator import Paginator

class PaginatorIterationTest(SimpleTestCase):
    def test_paginator_iteration_yields_pages(self):
        """
        Test that iterating over a Paginator object yields pages
        due to the presence of the __iter__ method.
        """
        object_list = list(range(1, 101))  # Sample object list
        paginator = Paginator(object_list, per_page=10)

        pages = list(paginator)
        self.assertEqual(len(pages), paginator.num_pages)
        for page in pages:
            self.assertTrue(hasattr(page, 'object_list'))
