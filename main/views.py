from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *

def home(r):
    return render(r, 'home.html', {
        'featured': Product.objects.filter(featured=True)[:8],
        'categories': Category.objects.all(),
        'brands': Brand.objects.all()})

def about(r):
    return render(r, 'about.html', {'brands': Brand.objects.all()})
def brands(r): return render(r, 'brands.html', {'brands': Brand.objects.all()})

def products(r):
    qs = Product.objects.select_related('brand', 'category')
    if r.GET.get('category'): qs = qs.filter(category__slug=r.GET['category'])
    if r.GET.get('brand'): qs = qs.filter(brand_id=r.GET['brand'])
    if r.GET.get('q'): qs = qs.filter(name__icontains=r.GET['q'])
    return render(r, 'products.html', {'products': qs,
        'categories': Category.objects.all(), 'brands': Brand.objects.all()})

def product_detail(r, pk):
    return render(r, 'product_detail.html', {'p': get_object_or_404(Product, pk=pk)})

def _form_view(request, form_class, template, msg):
    form = form_class(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, msg)
        return redirect(request.path)
    return render(request, template, {'form': form})

def dealer_register(r): return _form_view(r, DealerForm, 'dealer_register.html', 'Registration received. We will contact you soon.')
def enquiry(r): return _form_view(r, EnquiryForm, 'enquiry.html', 'Thank you! Our team will call you back.')
def contact(r): return _form_view(r, ContactForm, 'contact.html', 'Message sent successfully.')