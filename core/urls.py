from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('simple-register/', views.simple_register_view, name='simple_register'),
    path('login/', views.login_view, name='login'),
    path('login-new/', views.login_view, name='login_new'),
    path('logout/', views.logout_view, name='logout'),
    
    # User URLs
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/profile/edit/', views.user_profile_edit, name='user_profile_edit'),
    path('user/profile/card/', views.user_profile_card, name='user_profile_card'),
    path('user/jobs/', views.user_job_opportunities, name='user_job_opportunities'),
    path('user/change-password/', views.change_password, name='change_password'),
    path('user/documents/', views.user_documents, name='user_documents'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin/users/detail/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/users/create/', views.admin_create_user, name='admin_create_user'),
    path('admin/companies/', views.admin_manage_companies, name='admin_manage_companies'),
    path('admin/hr/', views.admin_manage_hr, name='admin_manage_hr'),
    path('admin/hr/edit/<int:user_id>/', views.admin_edit_hr, name='admin_edit_hr'),
    path('admin/security/', views.admin_manage_security, name='admin_manage_security'),
    path('admin/security/edit/<int:user_id>/', views.admin_edit_security, name='admin_edit_security'),
    path('admin/export/users/', views.admin_export_users, name='admin_export_users'),
    path('admin/export/users/template/', views.admin_export_users_template, name='admin_export_users_template'),
    path('admin/export/companies/', views.admin_export_companies, name='admin_export_companies'),
    path('admin/import/companies/', views.admin_import_companies, name='admin_import_companies'),
    path('admin/users/import/', views.admin_import_users, name='admin_import_users'),
    
    # Document management URLs
    path('admin/documents/', views.admin_manage_documents, name='admin_manage_documents'),
    path('admin/documents/create/', views.admin_create_document, name='admin_create_document'),
    path('admin/documents/create/<int:user_id>/', views.admin_create_document, name='admin_create_document_for_user'),
    path('admin/documents/edit/<int:document_id>/', views.admin_edit_document, name='admin_edit_document'),
    path('admin/documents/delete/<int:document_id>/', views.admin_delete_document, name='admin_delete_document'),
    path('admin/documents/import/', views.admin_import_documents, name='admin_import_documents'),
    path('admin/documents/export/', views.admin_export_documents, name='admin_export_documents'),
    path('admin/documents/export/template/', views.admin_export_documents_template, name='admin_export_documents_template'),
    
    # HR URLs
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/profile/', views.hr_profile, name='hr_profile'),
    path('hr/company/', views.hr_manage_company, name='hr_manage_company'),
    path('hr/jobs/', views.hr_manage_jobs, name='hr_manage_jobs'),
    path('hr/job-inquiries/', views.hr_job_inquiries, name='hr_job_inquiries'),
    
    # Security URLs
    path('security/dashboard/', views.security_dashboard, name='security_dashboard'),
    path('security/profile/', views.security_profile, name='security_profile'),
    path('security/add-user/', views.security_add_user, name='security_add_user'),
    path('security/scan-qr/', views.security_scan_qr, name='security_scan_qr'),
    
    # API URLs
    path('api/company-suggestions/', views.company_suggestions, name='company_suggestions'),
    
    # ID Card URL (accessible via QR code)
    path('IDCARD/<str:gsezid>/', views.idcard_view, name='idcard'),
    
    # Default URL (home page)
    path('', views.home_view, name='home'),
] 