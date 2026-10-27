import re

from django import forms
from django.forms import inlineformset_factory

from .models import FIRM_TYPE_DOCS, DEALER_DOCS, DEALER_DOC_LABELS, DealerRegistration, DealerPartner

MAX_PDF_MB = 5


def _clean_phone(value, label='Phone number'):
    digits = re.sub(r'\D', '', value or '')
    if digits.startswith('91') and len(digits) > 10:
        digits = digits[2:]
    digits = digits.lstrip('0') if len(digits) == 11 and digits.startswith('0') else digits
    if not 10 <= len(digits) <= 11:
        raise forms.ValidationError('Enter a valid %s (10 digits).' % label.lower())
    return digits


def _check_pdf(f):
    if f is None:
        return f
    if not f.name.lower().endswith('.pdf'):
        raise forms.ValidationError('Please upload a PDF file.')
    if f.size > MAX_PDF_MB * 1024 * 1024:
        raise forms.ValidationError('The PDF must be smaller than %d MB.' % MAX_PDF_MB)
    head = f.read(5)
    f.seek(0)
    if head != b'%PDF-':
        raise forms.ValidationError('This file is not a valid PDF.')
    return f


class DealerForm(forms.ModelForm):
    class Meta:
        model = DealerRegistration
        fields = ['company', 'firm_type', 'year_established', 'gst_number', 'pan_number',
                  'contact_person', 'phone', 'email', 'address', 'city', 'state', 'pincode',
                  'bank_name', 'bank_branch', 'account_holder', 'account_number', 'ifsc_code', 'account_type',
                  'payment_terms', 'id_proof_type', 'gst_certificate', 'id_proof', 'pan_card', 'cancelled_cheque',
                  'trade_licence', 'udyam_certificate', 'partnership_deed', 'firm_registration', 'llp_agreement',
                  'incorporation_certificate', 'moa_aoa', 'authorisation_letter', 'declaration_accepted']
        labels = {
            'company': 'Firm / company name', 'firm_type': 'Type of firm', 'year_established': 'Year of establishment',
            'gst_number': 'GST number', 'pan_number': 'PAN number', 'contact_person': 'Authorised person',
            'phone': 'Mobile number', 'email': 'Email address', 'address': 'Business address', 'city': 'City / town',
            'state': 'State', 'pincode': 'PIN code', 'bank_name': 'Bank name', 'bank_branch': 'Branch',
            'account_holder': 'Account holder name', 'account_number': 'Account number', 'ifsc_code': 'IFSC code',
            'account_type': 'Account type', 'payment_terms': 'Preferred payment terms (optional)',
            'id_proof_type': 'ID proof type', 'gst_certificate': 'GST certificate (PDF)',
            'id_proof': 'ID proof (PDF)',
            **{k: v + ' (PDF)' for k, v in DEALER_DOCS},
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'gst_certificate': forms.ClearableFileInput(attrs={'accept': 'application/pdf,.pdf'}),
            'id_proof': forms.ClearableFileInput(attrs={'accept': 'application/pdf,.pdf'}),
            **{k: forms.ClearableFileInput(attrs={'accept': 'application/pdf,.pdf'}) for k, _ in DEALER_DOCS},
            'year_established': forms.NumberInput(attrs={'placeholder': 'e.g. 2012', 'min': 1900, 'max': 2100}),
        }

    placeholders = {
        'company': 'e.g. ABC Computers', 'gst_number': '15-character GSTIN', 'pan_number': 'e.g. ABCDE1234F',
        'contact_person': 'Full name', 'phone': '10-digit mobile', 'email': 'name@company.com',
        'city': 'e.g. Kochi', 'pincode': '6 digits', 'bank_name': 'e.g. State Bank of India',
        'bank_branch': 'Branch name', 'account_holder': 'As in bank records', 'account_number': 'Account number',
        'ifsc_code': 'e.g. SBIN0001234',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required = ['company', 'firm_type', 'gst_number', 'pan_number', 'contact_person', 'phone', 'email', 'address',
                    'city', 'state', 'pincode', 'bank_name', 'bank_branch', 'account_holder', 'account_number',
                    'ifsc_code', 'account_type', 'id_proof_type', 'gst_certificate', 'id_proof', 'pan_card',
                    'cancelled_cheque', 'declaration_accepted']
        for name, f in self.fields.items():
            f.required = name in required
            if isinstance(f.widget, forms.Select):
                f.widget.attrs['class'] = 'form-select'
            elif isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs['class'] = 'form-check-input'
            else:
                f.widget.attrs['class'] = 'form-control'
            if name in self.placeholders:
                f.widget.attrs['placeholder'] = self.placeholders[name]
        self.fields['firm_type'].choices = [('', 'Select type')] + list(DealerRegistration._meta.get_field('firm_type').choices)
        self.fields['account_type'].choices = [('', 'Select type')] + list(DealerRegistration._meta.get_field('account_type').choices)
        self.fields['id_proof_type'].choices = [('', 'Select ID')] + list(DealerRegistration._meta.get_field('id_proof_type').choices)
        self.fields['payment_terms'].choices = [('', 'Select (optional)')] + list(DealerRegistration._meta.get_field('payment_terms').choices)
        self.fields['declaration_accepted'].label = ''

    def clean_gst_number(self):
        v = self.cleaned_data['gst_number'].strip().upper()
        if not re.fullmatch(r'\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]', v):
            raise forms.ValidationError('Enter a valid 15-character GST number.')
        return v

    def clean_pan_number(self):
        v = self.cleaned_data['pan_number'].strip().upper()
        if not re.fullmatch(r'[A-Z]{5}\d{4}[A-Z]', v):
            raise forms.ValidationError('Enter a valid 10-character PAN (e.g. ABCDE1234F).')
        return v

    def clean_ifsc_code(self):
        v = self.cleaned_data['ifsc_code'].strip().upper()
        if not re.fullmatch(r'[A-Z]{4}0[A-Z0-9]{6}', v):
            raise forms.ValidationError('Enter a valid 11-character IFSC code (e.g. SBIN0001234).')
        return v

    def clean_account_number(self):
        v = re.sub(r'\s', '', self.cleaned_data['account_number'])
        if not re.fullmatch(r'\d{9,18}', v):
            raise forms.ValidationError('Enter a valid account number (9 to 18 digits).')
        return v

    def clean_phone(self):
        return _clean_phone(self.cleaned_data['phone'], 'mobile number')

    def clean_pincode(self):
        v = self.cleaned_data['pincode'].strip()
        if not re.fullmatch(r'\d{6}', v):
            raise forms.ValidationError('Enter a 6-digit PIN code.')
        return v

    def clean_year_established(self):
        v = self.cleaned_data.get('year_established')
        if v and not 1900 <= v <= 2100:
            raise forms.ValidationError('Enter a valid year.')
        return v

    def clean_gst_certificate(self):
        return _check_pdf(self.cleaned_data.get('gst_certificate'))

    def clean_id_proof(self):
        return _check_pdf(self.cleaned_data.get('id_proof'))

    def clean_pan_card(self):
        return self._clean_doc('pan_card')

    def clean_cancelled_cheque(self):
        return self._clean_doc('cancelled_cheque')

    def clean_trade_licence(self):
        return self._clean_doc('trade_licence')

    def clean_udyam_certificate(self):
        return self._clean_doc('udyam_certificate')

    def clean_partnership_deed(self):
        return self._clean_doc('partnership_deed')

    def clean_firm_registration(self):
        return self._clean_doc('firm_registration')

    def clean_llp_agreement(self):
        return self._clean_doc('llp_agreement')

    def clean_incorporation_certificate(self):
        return self._clean_doc('incorporation_certificate')

    def clean_moa_aoa(self):
        return self._clean_doc('moa_aoa')

    def clean_authorisation_letter(self):
        return self._clean_doc('authorisation_letter')

    def _clean_doc(self, name):
        return _check_pdf(self.cleaned_data.get(name))

    def clean(self):
        data = super().clean()
        for name, mandatory in FIRM_TYPE_DOCS.get(data.get('firm_type'), []):
            f = data.get(name)
            if mandatory and not f and name not in self.errors:
                self.add_error(name, 'This document is required for %s.' % dict(DealerRegistration._meta.get_field('firm_type').choices)[data['firm_type']])
        return data

    def clean_declaration_accepted(self):
        if not self.cleaned_data.get('declaration_accepted'):
            raise forms.ValidationError('Please accept the declaration to continue.')
        return True


class PartnerForm(forms.ModelForm):
    class Meta:
        model = DealerPartner
        fields = ['name', 'mobile', 'address']
        labels = {'name': 'Name', 'mobile': 'Mobile (optional)', 'address': 'Residential address / city (optional)'}
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'mobile': forms.TextInput(attrs={'placeholder': '10-digit mobile'}),
            'address': forms.TextInput(attrs={'placeholder': 'Address, city'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'

    def clean_mobile(self):
        v = self.cleaned_data.get('mobile', '')
        return _clean_phone(v, 'mobile number') if v else ''


PartnerFormSet = inlineformset_factory(
    DealerRegistration, DealerPartner, form=PartnerForm,
    extra=0, min_num=1, max_num=5, validate_min=True, validate_max=True, can_delete=False)
