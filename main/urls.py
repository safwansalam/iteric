from django.urls import path
from . import views, dashboard

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('brands/', views.brands, name='brands'),
    path('dealer-registration/', views.dealer_register, name='dealer'),
    path('enquiry/', views.enquiry, name='enquiry'),
    path('contact/', views.contact, name='contact'),

    # staff dashboard
    path('dashboard/', dashboard.dashboard_home, name='dashboard_home'),
    path('dashboard/login/', dashboard.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', dashboard.dashboard_logout, name='dashboard_logout'),
    path('dashboard/<str:kind>/', dashboard.dashboard_list, name='dashboard_list'),
]