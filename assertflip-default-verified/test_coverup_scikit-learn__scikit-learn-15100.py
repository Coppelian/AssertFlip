import pytest
from sklearn.feature_extraction.text import strip_accents_unicode

def test_strip_accents_unicode_bug():
    # Test strings
    s1 = chr(241)  # "ñ" as a single code point
    s2 = chr(110) + chr(771)  # "n" followed by a combining tilde

    # Expected behavior: both should be stripped to "n"
    assert strip_accents_unicode(s1) == "n"
    
    # Correct the assertion to expose the bug
    assert strip_accents_unicode(s2) == "n"
