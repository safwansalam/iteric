from django.contrib import admin
from django.utils.html import format_html
from .models import (Category, Brand, Product, DealerRegistration, DealerPartner,
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


class PartnerInline(admin.TabularInline):
    model = DealerPartner
    extra = 0


@admin.register(DealerRegistration)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('company', 'contact_person', 'phone', 'city', 'status', 'created')
    list_filter = ('status', 'city')
    search_fields = ('company', 'contact_person', 'phone', 'gst_number')
    inlines = [PartnerInline]
    readonly_fields = ('gst_certificate', 'id_proof', 'pan_card', 'cancelled_cheque', 'trade_licence', 'udyam_certificate',
                       'partnership_deed', 'firm_registration', 'llp_agreement', 'incorporation_certificate',
                       'moa_aoa', 'authorisation_letter')   # documents are opened from the staff dashboard


admin.site.register([CustomerEnquiry, ContactMessage])
