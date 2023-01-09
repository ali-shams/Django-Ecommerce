import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)

from apps.account.repository.manager import UserManager
from painless.helper.enums import RegexPatternEnum
from painless.models import (
    TimeStampMixin,
    TruncateMixin,
)


class User(AbstractUser,
           TimeStampMixin,
           TruncateMixin):
    username = None
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = list()

    secret = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text=_("A user's token for sending emails "
                    "and OTP verification"),
    )
    first_name = models.CharField(
        _("first name"),
        max_length=30,
        validators=[MinLengthValidator(3),
                    MaxLengthValidator(30)],
        help_text=_("User's first name"),
    )
    last_name = models.CharField(
        _("last name"),
        max_length=30,
        validators=[MinLengthValidator(3),
                    MaxLengthValidator(30)],
        help_text=_("User's last name"),
    )

    dal = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.phone_number}"

    def __repr__(self):
        return f"{self.phone_number}"
