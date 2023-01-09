from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from apps.warehouse.repository.manager import \
    TagDataAccessLayerManager
from painless.models import (
    TitleSlugMixin,
    TimeStampMixin,
    TruncateMixin,
)


class Tag(TitleSlugMixin,
          TimeStampMixin,
          TruncateMixin):
    dal = TagDataAccessLayerManager()
    objects = models.Manager()

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    def save(self,
             *args,
             **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
