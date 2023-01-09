from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from apps.warehouse.repository.manager import \
    ProductDataAccessLayerManager
from painless.models import (
    SKUMixin,
    TitleSlugDescriptionMixin,
    TimeStampMixin,
    TruncateMixin,
)


class Product(SKUMixin,
              TitleSlugDescriptionMixin,
              TimeStampMixin,
              TruncateMixin):
    subtitle = models.CharField(
        _("subtitle"),
        max_length=255,
        help_text=_("Product subtitle"),
    )
    # ############################### #
    #            BooleanField         #
    # ############################### #
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Is this product active/available on the website"),
    )
    is_voucher_active = models.BooleanField(
        _("is voucher active"),
        default=False,
        help_text=_("Is this product has a discount/voucher/offer "
                    "on the website"),
    )
    details = models.JSONField(
        _("details"),
        default=dict,
        help_text=_("Dynamic detail of the product"),
    )
    # ############################### #
    #                 Fks             #
    # ############################### #
    brand = models.ForeignKey(
        "Brand",
        verbose_name=_("brand"),
        related_name="products",
        null=True,
        on_delete=models.SET_NULL,
        help_text=_("Access to the related brand of a product"),
    )
    category = models.ForeignKey(
        "Category",
        verbose_name=_("category"),
        related_name="products",
        null=True,
        on_delete=models.PROTECT,
        help_text=_("Access to the related category of a product"),
    )
    tags = models.ManyToManyField(
        "Tag",
        verbose_name=_("tags"),
        related_name="products",
        help_text=_("Access to the related tag(s) of a product"),
    )

    dal = ProductDataAccessLayerManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    def save(self,
             *args,
             **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class ProductShowCase(Product):
    class Meta:
        proxy = True
        verbose_name = _("Product ShowCase")
        verbose_name_plural = _("Product ShowCases")
