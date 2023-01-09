from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MaxLengthValidator,
)

from apps.feedback.repository.manager import \
    ReviewDataAccessLayerManager
from painless.models import (
    TimeStampMixin,
    TruncateMixin,
)


class Review(TimeStampMixin,
             TruncateMixin):
    title = models.CharField(
        _("title"),
        max_length=50,
        validators=[MaxLengthValidator(50)],
        help_text=_("User's review title"),
    )
    rate = models.FloatField(
        _("rate"),
        validators=[MinValueValidator(1),
                    MaxValueValidator(5)],
        help_text=_("User's review rate"),
    )
    email = models.EmailField(
        _("email"),
        help_text=_("User's email to submit review"),
    )
    message = models.TextField(
        _("message"),
        help_text=_("User's review message"),
    )
    # ############################### #
    #                 Fks             #
    # ############################### #
    product = models.ForeignKey(
        "warehouse.Product",
        verbose_name=_("product"),
        related_name="reviews",
        on_delete=models.CASCADE,
        help_text=_("Access to the related product of a review"),
    )

    dal = ReviewDataAccessLayerManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")

    def __str__(self):
        return f"{self.id}"

    def __repr__(self):
        return f"{self.id}"
