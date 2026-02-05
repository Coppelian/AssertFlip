import pytest

def test_capfd_includes_carriage_return(capfd):
    print('Test string with carriage return', end='\r')
    out, err = capfd.readouterr()
    assert out.endswith('\r')
