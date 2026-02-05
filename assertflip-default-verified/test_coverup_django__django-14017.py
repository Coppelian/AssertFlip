from django.test import SimpleTestCase
from django.db.models import Exists, Q
from django.contrib.auth.models import User  # Using User model for testing

class QExistsCommutativeTest(SimpleTestCase):
    def test_q_exists_commutative(self):
        """
        Test the commutative property of the & operator between Q and Exists.
        """
        # Create a Q object
        q_object = Q()

        # Create an Exists object using the User model
        exists_object = Exists(User.objects.all())

        # Test Exists & Q - should not raise an error
        try:
            result = exists_object & q_object
            self.assertIsInstance(result, Q)
        except TypeError:
            self.fail("Exists & Q raised TypeError unexpectedly")

        # Test Q & Exists - should not raise a TypeError
        try:
            result = q_object & exists_object
            self.assertIsInstance(result, Q)
        except TypeError:
            self.fail("Q & Exists raised TypeError unexpectedly")
