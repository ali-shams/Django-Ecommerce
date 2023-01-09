from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext_lazy as _

from painless.helper.typing import Byte


@deconstructible
class DimensionValidator(BaseValidator):
    def __init__(self,
                 width,
                 height):
        self.width = width
        self.height = height

    def __call__(self,
                 value):
        pic = value.file.open()
        width, height = get_image_dimensions(pic)
        if not (width == self.width and height == self.height):
            raise ValidationError(
                _(f"Expected dimension is: [{self.width}w, "
                  f"{self.height}h] "
                  f"but actual is: [{width}w, {height}h]"))
