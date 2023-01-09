from django.db import models
from django.utils.translation import gettext_lazy as _


class GenderStatus(models.TextChoices):
    Male = ('male', _('Male'))
    Female = ('female', _('Female'))
