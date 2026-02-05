from django.test import TestCase
from django.db.models import Q
from django.contrib.auth.models import User  # Using User model for testing

class TestXORLogic(TestCase):
    def setUp(self):
        # Create a user with a specific ID
        self.user = User.objects.create(id=37, username='testuser')

    def test_xor_logic_with_multiple_arguments(self):
        # Test with three identical Q objects combined with XOR
        count = User.objects.filter(Q(id=37) ^ Q(id=37) ^ Q(id=37)).count()
        # The expected behavior is that the count should be 1 because an odd number of true conditions should result in true
        self.assertEqual(count, 1)  # Correct behavior expected

    def tearDown(self):
        # Cleanup code if necessary
        self.user.delete()
