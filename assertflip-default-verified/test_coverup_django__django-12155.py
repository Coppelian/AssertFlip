from django.test import SimpleTestCase

class TrimDocstringTest(SimpleTestCase):
    def test_trim_docstring_with_non_empty_first_line(self):
        """
        Test trim_docstring with a docstring where the first line is not empty.
        """
        docstring = """This is a test docstring.
        It has multiple lines.
        """
        expected_output = "This is a test docstring.\nIt has multiple lines."

        # Call the trim_docstring function
        from django.contrib.admindocs.utils import trim_docstring
        output = trim_docstring(docstring)

        # Assert that the output is a non-empty string
        self.assertTrue(output)
        
        # The output should match the expected trimmed version of the docstring
        self.assertEqual(output, expected_output)
