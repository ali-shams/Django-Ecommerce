from django.db import models
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField


class Attribute(models.Model):
    title = models.CharField(
        _("title"),
        max_length=255,
        help_text=_("Attribute title"),
    )
    values = ArrayField(
        default=list,
        base_field=models.CharField(max_length=50),
    )
    # ############################### #
    #                 Fks             #
    # ############################### #
    category = models.ForeignKey(
        "category",
        verbose_name=_("category"),
        related_name="attributes",
        on_delete=models.CASCADE,
        help_text=_("Access to the related category of a attribute"),
    )

    class Meta:
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title
