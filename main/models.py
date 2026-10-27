import os
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models


def get_private_storage():
    """Dealer documents (GST certificate, ID proof) are kept OUTSIDE the public media folder."""
    return FileSystemStorage(location=str(settings.BASE_DIR / 'private_media'))


def dealer_upload(instance, filename):
    return 'dealers/%s.pdf' % uuid.uuid4().hex      # random name, original file name is not kept



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


FIRM_TYPES = [('proprietorship', 'Proprietorship'), ('partnership', 'Partnership'), ('llp', 'LLP'),
              ('private_ltd', 'Private Limited'), ('public_ltd', 'Public Limited'), ('other', 'Other')]
PAYMENT_TERMS = [('advance', 'Advance payment'), ('cheque', 'Current cheque'), ('pdc', 'Post-dated cheque'),
                 ('credit_7', 'Credit - 7 days'), ('credit_14', 'Credit - 14 days'),
                 ('credit_21', 'Credit - 21 days'), ('credit_30', 'Credit - 30 days')]
ACCOUNT_TYPES = [('current', 'Current'), ('cc', 'Cash Credit'), ('od', 'Overdraft'), ('savings', 'Savings')]
ID_TYPES = [('aadhaar', 'Aadhaar card'), ('pan', 'PAN card'), ('voter', 'Voter ID'),
            ('licence', 'Driving licence'), ('passport', 'Passport')]


# every private PDF a dealer can upload: (field name, label)
DEALER_DOCS = [
    ('gst_certificate', 'GST certificate'), ('pan_card', 'PAN card'), ('id_proof', 'ID proof'),
    ('cancelled_cheque', 'Cancelled cheque / bank proof'),
    ('trade_licence', 'Shop / trade licence'), ('udyam_certificate', 'Udyam registration'),
    ('partnership_deed', 'Partnership deed'), ('firm_registration', 'Firm registration certificate'),
    ('llp_agreement', 'LLP agreement'), ('incorporation_certificate', 'Certificate of incorporation'),
    ('moa_aoa', 'MOA and AOA'), ('authorisation_letter', 'Authorisation letter / board resolution'),
]
DEALER_DOC_LABELS = dict(DEALER_DOCS)
# extra documents per firm type: (field, mandatory?)
FIRM_TYPE_DOCS = {
    'proprietorship': [('trade_licence', True), ('udyam_certificate', False)],
    'partnership': [('partnership_deed', True), ('firm_registration', False)],
    'llp': [('llp_agreement', True), ('incorporation_certificate', True), ('authorisation_letter', True)],
    'private_ltd': [('incorporation_certificate', True), ('moa_aoa', True), ('authorisation_letter', True)],
    'public_ltd': [('incorporation_certificate', True), ('moa_aoa', True), ('authorisation_letter', True)],
}


class DealerRegistration(models.Model):
    # business
    company = models.CharField(max_length=200)
    firm_type = models.CharField(max_length=20, choices=FIRM_TYPES, blank=True)
    year_established = models.PositiveSmallIntegerField(null=True, blank=True)
    gst_number = models.CharField(max_length=15)
    pan_number = models.CharField(max_length=10, blank=True)
    # contact
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=60, blank=True, default='Kerala')
    pincode = models.CharField(max_length=6, blank=True)
    # bank
    bank_name = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    account_holder = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    ifsc_code = models.CharField(max_length=11, blank=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, blank=True)
    # terms + documents (PDF, stored privately)
    payment_terms = models.CharField(max_length=10, choices=PAYMENT_TERMS, blank=True)
    id_proof_type = models.CharField(max_length=10, choices=ID_TYPES, blank=True)
    gst_certificate = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    id_proof = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    pan_card = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    cancelled_cheque = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    trade_licence = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    udyam_certificate = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    partnership_deed = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    firm_registration = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    llp_agreement = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    incorporation_certificate = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    moa_aoa = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    authorisation_letter = models.FileField(upload_to=dealer_upload, storage=get_private_storage, blank=True)
    declaration_accepted = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=DEALER_STATUS, default='new')
    created = models.DateTimeField(auto_now_add=True)

    @property
    def ref(self):
        return 'ITE-D%04d' % self.pk

    def __str__(self):
        return self.company


class DealerPartner(models.Model):
    """Partners / proprietors of a dealer firm (up to 5 per registration)."""
    dealer = models.ForeignKey(DealerRegistration, on_delete=models.CASCADE, related_name='partners')
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


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
