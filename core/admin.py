from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, Document

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'gsezid', 'user_type', 'status', 'is_verified')
    list_filter = ('user_type', 'status', 'is_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'gsezid')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'middle_name', 'last_name', 'email', 'nationality', 'date_of_birth', 
                                     'gsez_card_issue_date', 'gsez_card_expiry_date', 'gsezid', 'profile_photo')}),
        ('Contact info', {'fields': ('emergency_contact_numbers', 'family_members')}),
        ('Address info', {'fields': ('current_address', 'is_permanent', 'permanent_address')}),
        ('Current Employment', {'fields': ('current_employer', 'current_employer_join_date', 'current_employer_emp_code',
                                          'current_employer_designation', 'current_employer_department', 'current_employer_company',
                                          'current_employer_remarks', 'current_employer_rating')}),
        ('Previous Employment', {'fields': ('previous_employers',)}),
        ('Education', {'fields': ('qualifications',)}),
        ('Status', {'fields': ('status', 'is_verified', 'qr_code', 'user_type', 'is_required_profile_detail', 'is_printed')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'gsezid', 'nationality', 'date_of_birth', 'user_type'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make all fields non-required
        if form.base_fields:
            for field_name in form.base_fields:
                if field_name not in ['password1', 'password2']:
                    form.base_fields[field_name].required = False
        return form

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'govt_id_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'govt_id_number')
    list_filter = ('user__user_type',)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name',)
    search_fields = ('company_name',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Company, CompanyAdmin)
