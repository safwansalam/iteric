import csv

from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from .models import (ContactMessage, CustomerEnquiry, DealerRegistration,
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
        fields=['company', 'contact_person', 'phone', 'email', 'gst_number', 'city', 'address'],
        search=['company', 'contact_person', 'phone', 'email', 'gst_number', 'city']),
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
        w.writerow(cfg['fields'] + ['status', 'received'])
        for o in qs:
            w.writerow([getattr(o, f) for f in cfg['fields']] +
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