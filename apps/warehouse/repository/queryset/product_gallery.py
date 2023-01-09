from django.db.models import (
    QuerySet,
)


class ProductGalleryQuerySet(QuerySet):

    def get_default(self):
        """Get all default galleries"""
        return self.filter(is_default=True)
