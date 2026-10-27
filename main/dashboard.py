import csv

from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import (DEALER_DOCS, DEALER_DOC_LABELS, FIRM_TYPE_DOCS, ContactMessage, CustomerEnquiry, DealerRegistration,
                     ENQUIRY_STATUS, DEALER_STATUS)

staff_only = user_passes_test(lambda u: u.is_active and u.is_staff,
                              login_url='dashboard_login')

# one entry per page of the dashboard
KINDS = {
    'enquiries': dict(
        model=CustomerEnquiry, title='Customer Enquiries', icon='bi-chat-dots',
        statuses=ENQUIRY_STATUS,
        fields=['name', 'phone', 'email', 'product_interest', 'message'],
        search=['name', 'phone', 'email', 'product_interest', 'message']),
    'contacts': dict(
        model=ContactMessage, title='Contact Messages', icon='bi-envelope',
        statuses=ENQUIRY_STATUS,
        fields=['name', 'email', 'subject', 'message'],
        search=['name', 'email', 'subject', 'message']),
    'dealers': dict(
        model=DealerRegistration, title='Dealer Registrations', icon='bi-shop',
        statuses=DEALER_STATUS,
        fields=['company', 'contact_person', 'phone', 'email', 'gst_number', 'city'],
        export_fields=['company', 'firm_type', 'year_established', 'gst_number', 'pan_number', 'contact_person', 'phone',
                       'email', 'address', 'city', 'state', 'pincode', 'bank_name', 'bank_branch', 'account_holder',
                       'account_number', 'ifsc_code', 'account_type', 'payment_terms', 'id_proof_type'],
        search=['company', 'contact_person', 'phone', 'email', 'gst_number', 'pan_number', 'city']),
}


def _nav():
    return [dict(key=k, title=v['title'], icon=v['icon'],
                 new=v['model'].objects.filter(status='new').count())
            for k, v in KINDS.items()]


@staff_only
def dashboard_home(request):
    cards = []
    for key, cfg in KINDS.items():
        qs = cfg['model'].objects.all()
        cards.append(dict(key=key, title=cfg['title'], icon=cfg['icon'],
                          total=qs.count(), new=qs.filter(status='new').count(),
                          recent=qs.order_by('-created')[:5]))
    return render(request, 'dashboard/home.html',
                  {'cards': cards, 'nav': _nav(), 'active': 'home'})


@staff_only
def dashboard_list(request, kind):
    cfg = KINDS.get(kind)
    if not cfg:
        raise Http404
    Model = cfg['model']

    # change status from the table
    if request.method == 'POST':
        obj = Model.objects.filter(pk=request.POST.get('id')).first()
        new_status = request.POST.get('status')
        if obj and new_status in dict(cfg['statuses']):
            obj.status = new_status
            obj.save(update_fields=['status'])
        return redirect(request.POST.get('next') or request.path)

    qs = Model.objects.order_by('-created')
    status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()
    if status in dict(cfg['statuses']):
        qs = qs.filter(status=status)
    else:
        status = ''
    if q:
        cond = Q()
        for f in cfg['search']:
            cond |= Q(**{f + '__icontains': q})
        qs = qs.filter(cond)

    if request.GET.get('export'):
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="{kind}.csv"'
        w = csv.writer(resp)
        cols = cfg.get('export_fields', cfg['fields'])
        w.writerow(cols + ['status', 'received'])
        for o in qs:
            w.writerow([getattr(o, f) for f in cols] +
                       [o.status, o.created.strftime('%d-%m-%Y %H:%M')])
        return resp

    page = Paginator(qs, 15).get_page(request.GET.get('page'))
    rows = [dict(obj=o, values=[(f.replace('_', ' ').title(), getattr(o, f)) for f in cfg['fields']])
            for o in page]
    return render(request, 'dashboard/list.html', {
        'cfg': cfg, 'kind': kind, 'page': page, 'rows': rows, 'statuses': cfg['statuses'],
        'status': status, 'q': q, 'nav': _nav(), 'active': kind,
        'next': request.get_full_path(),
    })


# ---------- login / logout (staff accounts only) ----------
class StaffLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError('No dashboard access.', code='no_access')


class DashboardLoginView(LoginView):
    template_name = 'dashboard/login.html'
    authentication_form = StaffLoginForm
    redirect_authenticated_user = False

    def get_success_url(self):
        return self.get_redirect_url() or '/dashboard/'


dashboard_login = DashboardLoginView.as_view()
dashboard_logout = LogoutView.as_view(next_page='dashboard_login')


# ---------- dealer application: full details + private documents ----------
DEALER_SECTIONS = [
    ('Business', 'bi-building', [('Firm / company', 'company'), ('Type of firm', 'firm_type_label'),
                                 ('Year established', 'year_established'), ('GST number', 'gst_number'),
                                 ('PAN number', 'pan_number')]),
    ('Contact', 'bi-geo-alt', [('Authorised person', 'contact_person'), ('Mobile', 'phone'), ('Email', 'email'),
                               ('Address', 'address'), ('City', 'city'), ('State', 'state'), ('PIN code', 'pincode')]),
    ('Bank details', 'bi-bank', [('Bank', 'bank_name'), ('Branch', 'bank_branch'), ('Account holder', 'account_holder'),
                                 ('Account number', 'account_number'), ('IFSC', 'ifsc_code'),
                                 ('Account type', 'account_type_label'), ('Preferred payment terms', 'payment_terms_label')]),
]


@staff_only
def dashboard_dealer(request, pk):
    d = get_object_or_404(DealerRegistration, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(DEALER_STATUS):
            d.status = new_status
            d.save(update_fields=['status'])
        return redirect(request.path)
    d.firm_type_label = d.get_firm_type_display()
    d.account_type_label = d.get_account_type_display()
    d.payment_terms_label = d.get_payment_terms_display()
    sections = [dict(title=t, icon=i, rows=[(l, getattr(d, a) or '—') for l, a in rows]) for t, i, rows in DEALER_SECTIONS]
    return render(request, 'dashboard/dealer_detail.html', {
        'docs': [(label, key, bool(getattr(d, key))) for key, label in DEALER_DOCS if getattr(d, key) or key in required_docs(d)],
        'd': d, 'sections': sections, 'partners': d.partners.all(), 'statuses': DEALER_STATUS,
        'nav': _nav(), 'active': 'dealers',
    })


def required_docs(d):
    base = ['gst_certificate', 'pan_card', 'id_proof', 'cancelled_cheque']
    return base + [n for n, _ in FIRM_TYPE_DOCS.get(d.firm_type, [])]


@staff_only
def dashboard_dealer_file(request, pk, which):
    d = get_object_or_404(DealerRegistration, pk=pk)
    which = {'gst': 'gst_certificate', 'id': 'id_proof'}.get(which, which)
    if which not in DEALER_DOC_LABELS:
        raise Http404
    f = getattr(d, which)
    if not f:
        raise Http404
    try:
        fh = f.open('rb')
    except FileNotFoundError:
        raise Http404
    resp = FileResponse(fh, content_type='application/pdf')
    name = DEALER_DOC_LABELS[which].split(' /')[0].replace(' ', '-')
    resp['Content-Disposition'] = 'inline; filename="%s-%s.pdf"' % (name, d.ref)
    resp['X-Content-Type-Options'] = 'nosniff'
    return resp
