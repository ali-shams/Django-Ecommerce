from modeltranslation.translator import (
    register,
    TranslationOptions
)

from warehouse.models import Attribute


@register(Attribute)
class AttributeTranslationOptions(TranslationOptions):
    fields = (
        'title',
    )
    required_languages = (
        'en',
    )
