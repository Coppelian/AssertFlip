import pytest
import astropy.coordinates as coord

class CustomCoord(coord.SkyCoord):
    @property
    def prop(self):
        return self.random_attr

def test_custom_coord_property_access_bug():
    c = CustomCoord('00h42m30s', '+41d12m00s', frame='icrs')
    try:
        _ = c.prop
    except AttributeError as e:
        # Correct behavior should indicate 'random_attr' is missing
        assert "'CustomCoord' object has no attribute 'random_attr'" in str(e)
