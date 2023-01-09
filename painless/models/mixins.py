import secrets

from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from khayyam import JalaliDatetime
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import (
    models,
    connection
)
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator
)
from sorl.thumbnail import (
    ImageField,
    get_thumbnail
)

from kernel.settings.packages import DEFAULT_CURRENCY_SHOW_ON_SITE
from painless.helper.typing import Dimension


class TitleSlugMixin(models.Model):
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args,
                         **kwargs)
        # Dynamically change help text
        self.__class__.title.field.help_text = _("{0} title".format(self.__class__.__name__.capitalize()))  # noqa

    title = models.CharField(
        _("title"),
        max_length=255,
        unique=True
    )
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        unique=True,
        editable=False,
        allow_unicode=True,
        help_text=_("Slug is a newspaper term. A short label for "
                    "something containing only letters, numbers, underscores, "
                    "or hyphens. They are generally used in URLs"),
    )

    @admin.display(description=_("title"), ordering=("-title"))
    def get_title(self):
        return self.title if len(self.title) < 30 else (self.title[:30] + "...")

    class Meta:
        abstract = True


class TimeStampMixin(models.Model):
    created = models.DateTimeField(
        _("created"),
        auto_now_add=True,
        help_text=_("Automatic registration of record creation time "
                    "in the database"),
    )

    @admin.display(description=_("created"), ordering=("-created"))
    def get_gregorian_created(self):
        return self.created.strftime("%Y-%m-%d")

    class Meta:
        abstract = True


class UploadBasePictureMixin(models.Model):
    picture = models.ImageField(
        _("picture"),
        upload_to="not-config",
        width_field="width_field",
        height_field="height_field",
        help_text=_("The picture that is uploaded"),
    )

    class Meta:
        abstract = True


class UploadNullAblePictureMixin(UploadBasePictureMixin):

    def get_picture_field(self):
        field = models.ImageField(
            _("picture"),
            upload_to=self.upload_path,
            width_field="width_field",
            height_field="height_field",
            max_length=110,
            validators=[*self.get_validators()],
            help_text=_("The picture that is uploaded")
        )
        return field

    class Meta:
        abstract = True


class TruncateMixin:
    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE '{0}' CASCADE".format(cls._meta.db_table))  # noqa
