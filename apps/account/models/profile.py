from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MaxLengthValidator

from apps.account.repository.manager import \
    ProfileDataAccessLayerManager
from apps.account.helper.enums import GenderStatus
from painless.models import (
    TimeStampMixin,
    TruncateMixin,
)


class Profile(TimeStampMixin,
              TruncateMixin):
    national_code = models.CharField(
        _("national code"),
        max_length=10,
        validators=[MaxLengthValidator(10)],
        help_text=_("National ID"),
    )
    gender = models.CharField(
        _("gender"),
        choices=GenderStatus.choices,
        null=True,
        max_length=10,
        validators=[MaxLengthValidator(10)],
        help_text=_("Users' gender"),
    )
    # ############################### #
    #            BooleanField         #
    # ############################### #
    is_complete = models.BooleanField(
        _("is complete"),
        default=False,
        blank=True,
        help_text=_("Whether the user profile is complete or not"),
    )
    # ############################### #
    #                 Fks             #
    # ############################### #
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        related_name="profile",
        on_delete=models.PROTECT,
        help_text=_("The user this profile belongs to"),
    )

    dal = ProfileDataAccessLayerManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.phone_number

    def __repr__(self):
        return self.user.phone_number
