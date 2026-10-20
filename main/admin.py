from django.contrib import admin
from django.utils.html import format_html
from .models import (Category, Brand, Product, DealerRegistration,
                     CustomerEnquiry, ContactMessage)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview',)

    @admin.display(description='Logo')
    def logo_preview(self, obj):
        return format_html('<img src="{}" style="height:40px">', obj.logo.url)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'featured')
    list_filter = ('category', 'brand', 'featured')


admin.site.register([DealerRegistration, CustomerEnquiry, ContactMessage])