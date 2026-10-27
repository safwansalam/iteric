from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *
from .dealer_forms import DealerForm, PartnerFormSet   # new dealer form (overrides the old one)
from django.db import transaction


def home(r):
    # featured products first, then the newest ones, 12 in total (3 rows of 4)
    products = Product.objects.select_related('brand').order_by('-featured', '-id')[:12]
    return render(r, 'home.html', {
        'featured': products,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all()})


def about(r):
    return render(r, 'about.html', {'brands': Brand.objects.all()})


def brands(r):
    return render(r, 'brands.html', {'brands': Brand.objects.all()})


def products(r):
    qs = Product.objects.select_related('brand', 'category')
    sel_cat = r.GET.get('category', '')
    sel_brand = r.GET.get('brand', '')
    if sel_cat:
        qs = qs.filter(category__slug=sel_cat)
    if sel_brand.isdigit():
        qs = qs.filter(brand_id=sel_brand)
    return render(r, 'products.html', {
        'products': qs,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'sel_cat': sel_cat,
        'sel_brand': sel_brand if sel_brand.isdigit() else '',
    })


def product_detail(r, pk):
    return render(r, 'product_detail.html', {'p': get_object_or_404(Product, pk=pk)})


def _form_view(request, form_class, template, msg):
    form = form_class(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, msg)
        return redirect(request.path)
    return render(request, template, {'form': form})


def dealer_register(request):
    form = DealerForm(request.POST or None, request.FILES or None)
    formset = PartnerFormSet(request.POST or None, instance=None, prefix='partners')
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            dealer = form.save()
            formset.instance = dealer
            formset.save()
        messages.success(request, 'Thank you! Your dealer registration has been received (Reference: %s). '
                                  'Our team will verify your details and contact you soon.' % dealer.ref)
        return redirect('dealer')
    return render(request, 'dealer_register.html', {'form': form, 'formset': formset})
def enquiry(r): return _form_view(r, EnquiryForm, 'enquiry.html', 'Thank you! Our team will call you back.')
def contact(r): return _form_view(r, ContactForm, 'contact.html', 'Message sent successfully.')
