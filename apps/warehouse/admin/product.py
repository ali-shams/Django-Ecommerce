from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.contrib.admin.utils import unquote
from django.template.response import TemplateResponse

from sorl.thumbnail.admin import AdminImageMixin
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter,
    RelatedDropdownFilter,
    ChoiceDropdownFilter
)

from warehouse.admin.auto_complete_filter.filters import ( 
    CategoryFilter,
    BrandFilter,
)
from painless.admin.mixins import ReadOnlyAdminMixin
from warehouse.forms import ProductAttributeForm
from warehouse.resources import ProductResource
from warehouse.models import (
    Product,
    Pack,
    PhysicalInformation,
    ProductGallery,
    ProductShowCase
)


class PackInLine(admin.TabularInline):
    model = Pack
    fields = (
        'sku',
        'color',
        'warranty',
        'is_active',
        'is_default'
    )
    readonly_fields = (
        'sku',
    )
    extra = 0
    autocomplete_fields = (
        'color',
        'warranty'
    )
    show_change_link = True


class PhysicalInformationInLine(admin.TabularInline):
    model = PhysicalInformation
    fields = (
        'width',
        'height',
        'depth',
        'net_weight',
        'gross_weight'
    )
    extra = 0
    show_change_link = True


class GalleryInLine(AdminImageMixin, admin.StackedInline):
    model = ProductGallery
    fields = (
        'picture',
        'alternate_text',
    )
    readonly_fields = (
        'image_status',
    )
    extra = 0
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_form_template = 'admin/product_button.html'
    resource_class = ProductResource
    list_per_page = 10
    inlines = (
        PackInLine,
        PhysicalInformationInLine,
        GalleryInLine
    )
    list_select_related = (
        'brand',
        'category'
    )
    list_display = (
        'get_sku',
        'get_title',
        'brand',
        'category',
        'is_active',
        'is_voucher_active',
        'get_gregorian_created',
        'get_gregorian_modified',
        'get_solar_created',
        'get_solar_modified'
    )
    list_filter = (
        'is_active',
        'is_voucher_active',
        'created',
        'modified',
        BrandFilter,
        CategoryFilter,
        ('tags', RelatedDropdownFilter),
    )
    search_fields = (
        'title',
    )
    search_help_text = _('Search products by their title.')
    save_on_top = True
    list_editable = (
        'is_active',
        'is_voucher_active'
    )
    readonly_fields = (
        'sku',
        'slug',
        'created',
        'modified'
    )
    autocomplete_fields = (
        'brand',
        'category'
    )
    filter_horizontal = (  # or use filter_vertical
        'tags',
    )
    fieldsets = [
        (_('Basic Information'), {
            'fields': (
                'sku',
                'title',
                'title_en',
                'title_fa',
                'slug'
            )
        }),
        [_('Product Information'), {
            'classes': ('collapse',),
            'fields': [
                'subtitle',
                'description_en',
                'description_fa',
                'brand',
                'category',
                'tags',
            ]
        }],
        (_('Marketing'), {
            'classes': ('collapse',),
            'fields': (
                'is_active',
                'is_voucher_active'
            )
        }),
        (_('Security Center'), {
            'classes': ('collapse',),
            'fields': (
                'created',
                'modified'
            )
        })
    ]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['product_id'] = object_id
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def save_products_attributes(self, request, product):
        qs = product.category.attributes.all()
        list_keys = list(qs.values_list('title', flat=True))
        updated_data = dict()
        for key in list_keys:
            updated_data.update({key: request.POST.get(key)})
        product.details = updated_data
        product.save()

    def product_change_attributes(self, request, id, form_url=""):
        product = self.get_object(request, unquote(id))

        if request.method == 'POST':
            self.save_products_attributes(request, product)
            # TODO there is no validations for this form
            if request.POST.get('_continue'):
                return redirect('./')
            else:
                return redirect('../')

        IS_POPUP_VAR = "_popup"
        form = ProductAttributeForm(product)
        fieldsets = [(_("Detail of Product"), {"fields": list(form.fields.keys())})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            "title": _("Change Products Attributes"),
            "adminForm": adminForm,
            "form_url": form_url,
            "form": form,
            "is_popup": (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            "is_popup_var": IS_POPUP_VAR,
            "add": False,
            "change": True,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_add_permission": False,
            "has_view_permission": True,
            "has_editable_inline_admin_formsets": False,
            "has_absolute_url": False,
            "opts": self.model._meta,
            "original": product,
            "save_as": False,
            "show_save": True,
            **self.admin_site.each_context(request),
        }
        return TemplateResponse(
            request,
            "admin/product_change_attribute.html",
            context,
        )

    def get_urls(self):
        return [
            path(
                "<id>/attribute/",
                self.admin_site.admin_view(self.product_change_attributes),
                name="product_attribute",
            ),
        ] + super().get_urls()


@admin.register(ProductShowCase)
class ProductShowCaseAdmin(ProductAdmin, ReadOnlyAdminMixin):
    change_form_template = None
    list_display = (
        'id',
        'get_sku',
        'get_title',
        'brand',
        'category',
        'is_active',
        'is_voucher_active',
        'get_total_active_packs',
        'get_total_actual_count_stock_active_packs',
        'get_default_pack_price',
        'get_solar_modified'
    )

    def get_queryset(self, request):
        fields = (
            'id',
            'sku',
            'title',
            'brand__title',
            'category__title',
            'is_active',
            'is_voucher_active',
            'modified'
        )
        return Product.dal.get_available_items(fields=fields)

    @admin.display(description='total active packs', ordering='-total_active_packs')  # noqa
    def get_total_active_packs(self, obj):
        return obj.total_active_packs

    @admin.display(
        description='total actual count stock',
        ordering='-total_actual_count_stock')
    def get_total_actual_count_stock_active_packs(self, obj):
        return obj.total_actual_count_stock

    @admin.display(description='price', ordering='default_pack_price')
    def get_default_pack_price(self, obj):
        return f'{int(obj.default_pack_price.amount)} Rial'

    def get_urls(self):
        return super(ProductAdmin, self).get_urls()
