from django.test import TestCase
from django.test.utils import override_settings

from apps.account.models import (
    User,
    Profile,
)


@override_settings(LANGUAGE_CODE='en')
class ProfileModel(TestCase):
    """
    Test Profile-Model that should work properly
    ------

    - testing the magic methods : `__str__` and `__repr__`
    - testing `verbose_name` (single & plural)
    """

    @classmethod
    def setUpClass(cls):
        super(ProfileModel, cls).setUpClass()

        cls.user_one = User.objects.create(
            phone_number='+7-(963)-409-11-22'[:14],
            email='example@gmail.com',
            first_name='Mahmoud',
            last_name='Ahmadinejad',
            # date_joined=cls.get_random_time(),
            is_active=True,
            is_staff=False,
            is_superuser=False,
            password=1
        )
