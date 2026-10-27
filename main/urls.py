from django.urls import path
from main import dashboard, views

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
    path('dashboard/dealers/<int:pk>/', dashboard.dashboard_dealer, name='dashboard_dealer'),
    path('dashboard/dealers/<int:pk>/file/<str:which>/', dashboard.dashboard_dealer_file, name='dashboard_dealer_file'),
    path('dashboard/<str:kind>/', dashboard.dashboard_list, name='dashboard_list'),
]
