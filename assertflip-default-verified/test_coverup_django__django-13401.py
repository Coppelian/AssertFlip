from django.test import TestCase
from django.db import models

class AbstractModelA(models.Model):
    class Meta:
        abstract = True
    myfield = models.IntegerField()

class ConcreteModelB(AbstractModelA):
    class Meta:
        app_label = 'test_app'

class ConcreteModelC(AbstractModelA):
    class Meta:
        app_label = 'test_app'

class FieldEqualityTest(TestCase):
    def test_field_equality_bug(self):
        # Retrieve the field objects from both models
        field_b = ConcreteModelB._meta.get_field('myfield')
        field_c = ConcreteModelC._meta.get_field('myfield')

        # Add the field objects to a set
        field_set = {field_b, field_c}

        # Assert that the length of the set is 2, indicating the bug is fixed
        self.assertEqual(len(field_set), 2)
