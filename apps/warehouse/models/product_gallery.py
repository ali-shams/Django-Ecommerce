from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator

from apps.warehouse.repository.manager import \
    ProductGalleryDataAccessLayerManager
from apps.warehouse.helper.enums import ImageStatus
from painless.utils.upload_to import category_dir_path
from painless.utils.converters import UnitConvertor
from painless.helper.typing import MegaByte
from painless.models.validators import (
    DimensionValidator,
    ImageSizeValidator,
)
from painless.models import (
    UploadSorlThumbnailPictureMixin,
    TimeStampMixin,
    TruncateMixin,
)


class ProductGallery(UploadSorlThumbnailPictureMixin,
                     TimeStampMixin,
                     TruncateMixin):
    image_status = models.CharField(
        _("image status"),
        max_length=20,
        validators=[MaxLengthValidator(20)],
        choices=ImageStatus.choices,
        help_text=_("Determines what banner picture is on the website"),
    )
    # ############################### #
    #                 Fks             #
    # ############################### #
    product = models.ForeignKey(
        "Product",
        verbose_name=_("product"),
        related_name="galleries",
        on_delete=models.CASCADE,
        help_text=_("Access to the related product of a gallery"),
    )
    UploadSorlThumbnailPictureMixin._meta.get_field("picture").upload_to = \
        category_dir_path
    UploadSorlThumbnailPictureMixin._meta.get_field("picture").validators.extend(
        [
            DimensionValidator(800, 960),
            ImageSizeValidator(UnitConvertor.convert_megabyte_to_byte(MegaByte(1)))]
    )

    dal = ProductGalleryDataAccessLayerManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Gallery")
        verbose_name_plural = _("Galleries")

    def __str__(self):
        return f"{self.id}"

    def __repr__(self):
        return f"{self.id}"
