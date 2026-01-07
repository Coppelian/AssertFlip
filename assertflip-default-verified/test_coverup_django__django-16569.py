from django import forms
from django.test import SimpleTestCase
from django.conf import settings
from django.forms import formset_factory

# Ensure settings are configured only once
if not settings.configured:
    settings.configure(
        DEBUG=True,
        MIDDLEWARE_CLASSES=[],
        ROOT_URLCONF=__name__,
    )

class MyForm(forms.Form):
    my_field = forms.CharField()

class FormsetAddFieldsTest(SimpleTestCase):
    def test_add_fields_with_none_index(self):
        # Create a FormSet with can_delete=True and can_delete_extra=False
        MyFormSet = formset_factory(
            form=MyForm,
            can_delete=True,
            can_delete_extra=False,
        )
        my_formset = MyFormSet(initial=None)

        try:
            # Access the empty_form property to trigger the bug
            _ = my_formset.empty_form
        except TypeError as e:
            # If a TypeError is raised, the test should fail
            self.fail("TypeError raised: " + str(e))
