from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # login page
    path('', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register'),
    path('resetlink/',views.reset_email_page, name='resetemail'),
    path('reset/',views.reset_otp_page, name='resetotp'),
    path('resetpass/',views.reset_password_page, name='resetpass'),
    path('otpsend/',views.email_verification_password_reset, name='otpsend'),
    path('otp/',views.otp_verification_password_reset, name='otp'),
    path('savepass/',views.save_pass_password_reset, name='savepass'),
    path('login_user/', views.user_login, name='login'),
    path('signup/',views.user_signup,name='signup'),
    
    path('logout/', views.logout_user, name='logout'),

    #seller pages
    path('dashboard_seller/', views.seller_dashboard, name='dashboard_seller'),
    path('complains_seller/', views.complain_seller, name='complain_seller'),
    path('waiters/', views.waitermanagement, name='waiter_management'),

    #admin pages
    path('dashboard_admin/', views.admin_dashboard, name='dashboard_admin'),
    path('complains_admin/', views.complain_admin, name='complain_admin'),
    path('sellers/', views.sellermanagement, name='seller_management'),

    #student pages
    path('dashboard_student/', views.student_dashboard, name='dashboard_student'),
    path('complains_student/', views.complain_student, name='complain_student'),

    # others
    path('save-order/', views.save_order, name='save_order'),
    path('save-waiter/', views.save_waiter, name='save-waiter'),
    path('remove-waiter/', views.remove_waiter, name='remove-waiter'),
    path('save-seller/', views.save_seller, name='save-seller'),
    path('remove-seller/', views.remove_seller, name='remove-seller'),
    path('save-product/', views.save_product, name='save_product'),
    path('save_complain/', views.save_complain, name='save_complain'),
    path('update_complain_status/', views.update_complain_status, name='update_complain_status'),
]