from django import forms
from .models import DealerRegistration, CustomerEnquiry, ContactMessage

class BootstrapForm(forms.ModelForm):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'

class DealerForm(BootstrapForm):
    class Meta: model = DealerRegistration; fields = '__all__'

class EnquiryForm(BootstrapForm):
    class Meta: model = CustomerEnquiry; fields = '__all__'

class ContactForm(BootstrapForm):
    class Meta: model = ContactMessage; fields = '__all__'