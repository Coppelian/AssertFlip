from django.test import TestCase
from django.db.models import Q, Exists
from django.contrib.auth import get_user_model

class QDeconstructBugTest(TestCase):
    def test_deconstruct_with_exists_child(self):
        """
        Test deconstructing a Q object with a single Exists child.
        This should not raise a TypeError once the bug is fixed.
        """
        user_model = get_user_model()
        exists_expression = Exists(user_model.objects.filter(username='jim'))
        q_object = Q(exists_expression)

        try:
            q_object.deconstruct()
        except TypeError as e:
            self.fail(f"TypeError raised: {e}")
