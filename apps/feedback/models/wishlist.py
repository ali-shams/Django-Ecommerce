from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.feedback.repository.manager import \
    WishListDataAccessLayerManager
from painless.models import (
    TimeStampMixin,
    TruncateMixin,
)


class WishList(TimeStampMixin,
               TruncateMixin):
    # ############################### #
    #                 Fks             #
    # ############################### #
    user = models.OneToOneField(
        "account.User",
        verbose_name=_("user"),
        related_name="wishlist",
        null=True,
        on_delete=models.SET_NULL,
        help_text=_("The user this wishlist belongs to"),
    )
    products = models.ManyToManyField(
        "warehouse.Product",
        verbose_name=_("products"),
        related_name="wishlists",
        help_text=_("Access to the related product(s) of a wishlist"),
    )

    dal = WishListDataAccessLayerManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("WishList")
        verbose_name_plural = _("WishLists")

    def __str__(self):
        return self.user.phone_number

    def __repr__(self):
        return self.user.phone_number
