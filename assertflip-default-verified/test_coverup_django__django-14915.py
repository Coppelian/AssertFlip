from django.test import SimpleTestCase
from django.forms.models import ModelChoiceIteratorValue

class ModelChoiceIteratorValueHashableTest(SimpleTestCase):
    def test_model_choice_iterator_value_unhashable(self):
        """
        Test that using ModelChoiceIteratorValue as a dictionary key does not raise TypeError.
        """
        value_instance = ModelChoiceIteratorValue(value=1, instance=None)
        
        try:
            # Attempt to use ModelChoiceIteratorValue as a dictionary key
            test_dict = {value_instance: "test"}
        except TypeError as e:
            # If a TypeError is raised, the test should fail
            self.fail(f"ModelChoiceIteratorValue should be hashable, but raised TypeError: {str(e)}")
