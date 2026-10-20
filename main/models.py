import os
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Brand(models.Model):
    """A brand is just its logo (no name field)."""
    logo = models.ImageField(upload_to='brands/')

    def __str__(self):
        # shown in admin lists/dropdowns: the logo's file name, e.g. "hp.png"
        return os.path.basename(self.logo.name) if self.logo else f'Brand {self.pk}'


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


ENQUIRY_STATUS = [('new', 'New'), ('contacted', 'Contacted'), ('closed', 'Closed')]
DEALER_STATUS = [('new', 'New'), ('approved', 'Approved'), ('rejected', 'Rejected')]


class DealerRegistration(models.Model):
    company = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    gst_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=DEALER_STATUS, default='new')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company


class CustomerEnquiry(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    product_interest = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=ENQUIRY_STATUS, default='new')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=ENQUIRY_STATUS, default='new')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.subject}'