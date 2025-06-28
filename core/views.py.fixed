from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
import json
import qrcode
from io import BytesIO
import csv
import xlwt
from openpyxl import Workbook
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from PIL import Image
from django.core.files import File
import re
import os
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import uuid
import base64

from .models import User, Company, Document, generate_gsezid
from .forms import (
    UserRegistrationForm, UserProfileForm, DocumentForm, 
    CompanyForm, UserManagementForm, CustomAuthenticationForm,
    AdminUserEditForm, AdminUserCreationForm, SimpleUserRegistrationForm
)

# Helper functions for user type checks
def is_admin(user):
    return user.user_type == 'admin'

def is_hr(user):
    return user.user_type == 'hr'

def is_security(user):
    return user.user_type == 'security'

def is_regular_user(user):
    return user.user_type == 'user'

# Authentication views
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'user'  # Default user type
            user.save()
            messages.success(request, f'Account created successfully. Your GSEZ ID is {user.gsezid}. You can now login using this ID.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def simple_register_view(request):
    if request.method == 'POST':
        form = SimpleUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # First create the user without saving to the database
                user = form.save(commit=False)
                user.user_type = 'user'  # Default user type
                
                # Set default values for all potentially required fields
                user.nationality = 'Not Specified'
                user.current_address = 'Not Provided'
                
                # Use the new GSEZ ID format
                user.gsezid = generate_gsezid()
                
                # Save user
                user.save()
                
                messages.success(request, f'Account created successfully. Your GSEZ ID is {user.gsezid}. You can now login using this ID.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    else:
        form = SimpleUserRegistrationForm()
    return render(request, 'core/simple_register.html', {'form': form})

import json
from django.http import HttpResponse

def login_view(request):
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    # Check if this is a fallback from AJAX to traditional submission
    use_traditional_submit = request.POST.get('use_traditional_submit') == 'true'
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            # The form.clean() method has already authenticated the user at this point
            user = form.user_cache
            
            if user is not None:
                # Log the user in
                login(request, user)
                messages.success(request, f'Welcome, {user.first_name}!')
                
                # Get redirect URL based on user type
                redirect_url = 'user_dashboard'
                if user.user_type == 'admin':
                    redirect_url = 'admin_dashboard'
                elif user.user_type == 'hr':
                    redirect_url = 'hr_dashboard'
                elif user.user_type == 'security':
                    redirect_url = 'security_dashboard'
                
                # If it's an AJAX request and not a fallback, return JSON response
                if is_ajax and not use_traditional_submit:
                    try:
                        response_data = {
                            'success': True,
                            'redirect_url': str(reverse_lazy(redirect_url)),
                            'user_details': {
                                'gsezid': user.gsezid,
                                'name': user.get_full_name(),
                                'email': user.email,
                                'user_type': user.user_type
                            }
                        }
                        
                        # Return a proper JSON response with content type
                        return JsonResponse(response_data)
                    except Exception as e:
                        # Log the error and return a simple JSON error response
                        print(f"Error creating JSON response: {e}")
                        return JsonResponse({'success': False, 'message': 'Server error occurred'})
                
                # Otherwise, redirect as usual
                return redirect(redirect_url)
        else:
            # Form validation failed, error messages are attached to the form
            
            # If it's an AJAX request and not a fallback, return JSON response with errors
            if is_ajax and not use_traditional_submit:
                try:
                    errors_dict = {}
                    for field, error_list in form.errors.items():
                        errors_dict[field] = [str(error) for error in error_list]
                    
                    # Create a single error message for display
                    error_message = "An error occurred during login. Please try again."
                    if '__all__' in form.errors:
                        error_message = form.errors['__all__'][0]
                    
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'errors': errors_dict
                    })
                except Exception as e:
                    # Log the error and return a simple JSON error response
                    print(f"Error creating JSON response: {e}")
                    return JsonResponse({'success': False, 'message': 'Server error occurred'})
            
            # For standard form submission, add error message
            if not messages.get_messages(request):  # Only add if no messages exist
                if '__all__' in form.errors:
                    messages.error(request, form.errors['__all__'][0])
                else:
                    messages.error(request, 'An error occurred during login. Please try again.')
            
            # Return the form with the data to preserve input
            return render(request, 'core/login.html', {'form': form})
    else:
        form = CustomAuthenticationForm(request=request)
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# User Dashboard
@login_required
@user_passes_test(is_regular_user)
def user_dashboard(request):
    emergency_contacts = {
        'fire': '101',
        'police': '100',
        'ambulance': '108',
        'admin': '+91 9876543210',
        'security': '+91 9876543211'
    }
    return render(request, 'core/user/dashboard.html', {
        'user': request.user,
        'emergency_contacts': emergency_contacts
    })

@login_required
@user_passes_test(is_regular_user)
def user_profile(request):
    documents = Document.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        document_form = DocumentForm(request.POST, request.FILES)
        
        if form.is_valid() and (not document_form.has_changed() or document_form.is_valid()):
            form.save()
            
            if document_form.has_changed() and document_form.is_valid():
                document = document_form.save(commit=False)
                document.user = request.user
                document.save()
                
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
        document_form = DocumentForm()
    
    return render(request, 'core/user/profile_card.html', {
        'form': form,
        'document_form': document_form,
        'documents': documents
    })

@login_required
@user_passes_test(is_regular_user)
def user_profile_edit(request):
    # Process JSON fields for display
    emergency_contacts = request.user.get_emergency_contacts()
    family_members = request.user.get_family_members()
    previous_employers = request.user.get_previous_employers() 
    qualifications = request.user.get_qualifications()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        
        # Check if we have a camera capture image data
        camera_capture_data = request.POST.get('camera_capture_data')
        if camera_capture_data and camera_capture_data.startswith('data:image'):
            try:
                # Process the base64 image data
                format, imgstr = camera_capture_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Convert base64 to file
                import base64
                from django.core.files.base import ContentFile
                
                # Create a ContentFile from the decoded base64 data
                filename = f"{request.user.gsezid}.{ext}" if request.user.gsezid else f"user_{request.user.id}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=filename)
                
                # Assign the file to the user's profile_photo field
                request.user.profile_photo.save(filename, data, save=False)
                
                # Set the profile_full_link field with .jpg extension
                request.user.profile_full_link = f"http://207.108.234.113:83/{request.user.gsezid}.jpg"
                
            except Exception as e:
                print(f"Error processing camera capture data: {e}")
        elif 'profile_photo' in request.FILES:
            # If a profile photo was uploaded via the form, set the profile_full_link with .jpg extension
            request.user.profile_full_link = f"http://207.108.234.113:83/{request.user.gsezid}.jpg"
        
        # Check for deleted items
        deleted_contacts = request.POST.getlist('deleted_contacts[]', [])
        deleted_family_members = request.POST.getlist('deleted_family_members[]', [])
        deleted_employers = request.POST.getlist('deleted_employers[]', [])
        deleted_qualifications = request.POST.getlist('deleted_qualifications[]', [])
        
        # Process extra items
        contact_names_extra = request.POST.getlist('emergency_contact_name_extra[]', [])
        contact_numbers_extra = request.POST.getlist('emergency_contact_number_extra[]', [])
        
        family_names_extra = request.POST.getlist('family_member_name_extra[]', [])
        family_relations_extra = request.POST.getlist('family_member_relation_extra[]', [])
        family_numbers_extra = request.POST.getlist('family_member_number_extra[]', [])
        
        employer_names_extra = request.POST.getlist('previous_employer_name_extra[]', [])
        employer_join_dates_extra = request.POST.getlist('previous_employer_join_date_extra[]', [])
        employer_leave_dates_extra = request.POST.getlist('previous_employer_leave_date_extra[]', [])
        employer_remarks_extra = request.POST.getlist('previous_employer_remarks_extra[]', [])
        employer_ratings_extra = request.POST.getlist('previous_employer_rating_extra[]', [])
        
        qualification_names_extra = request.POST.getlist('qualification_extra[]', [])
        institution_names_extra = request.POST.getlist('institution_extra[]', [])
        year_of_passings_extra = request.POST.getlist('year_of_passing_extra[]', [])
        
        if form.is_valid():
            user = form.save(commit=False)
            
            # Process emergency contacts
            if deleted_contacts:
                updated_contacts = []
                for i, contact in enumerate(emergency_contacts):
                    if str(i) not in deleted_contacts:
                        updated_contacts.append(contact)
                user.set_emergency_contacts(updated_contacts)
            
            # Add extra emergency contacts
            for i in range(len(contact_names_extra)):
                if contact_names_extra[i] and contact_numbers_extra[i]:
                    emergency_contacts = user.get_emergency_contacts()
                    emergency_contacts.append({
                        'name': contact_names_extra[i],
                        'number': contact_numbers_extra[i]
                    })
                    user.set_emergency_contacts(emergency_contacts)
            
            # Process family members
            if deleted_family_members:
                updated_members = []
                for i, member in enumerate(family_members):
                    if str(i) not in deleted_family_members:
                        updated_members.append(member)
                user.set_family_members(updated_members)
            
            # Process previous employers
            if deleted_employers:
                updated_employers = []
                for i, employer in enumerate(previous_employers):
                    if str(i) not in deleted_employers:
                        updated_employers.append(employer)
                user.set_previous_employers(updated_employers)
            
            # Process qualifications
            if deleted_qualifications:
                updated_qualifications = []
                for i, qualification in enumerate(qualifications):
                    if str(i) not in deleted_qualifications:
                        updated_qualifications.append(qualification)
                user.set_qualifications(updated_qualifications)
            
            # Add extra qualifications
            for i in range(len(qualification_names_extra)):
                if qualification_names_extra[i] and institution_names_extra[i]:
                    qualifications = user.get_qualifications()
                    qualifications.append({
                        'qualification': qualification_names_extra[i],
                        'institution': institution_names_extra[i] if i < len(institution_names_extra) else '',
                        'year': year_of_passings_extra[i] if i < len(year_of_passings_extra) else ''
                    })
                    user.set_qualifications(qualifications)
            
            user.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('user_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/user/profile_edit.html', {
        'form': form,
        'emergency_contacts': emergency_contacts,
        'family_members': family_members,
        'previous_employers': previous_employers,
        'qualifications': qualifications,
    })

@login_required
@user_passes_test(is_regular_user)
def user_profile_card(request):
    return render(request, 'core/user/profile_card.html', {'user': request.user})

# ID Card Views
def idcard_view(request, gsezid):
    """
    View for displaying a user's ID card based on their GSEZ ID.
    This view is publicly accessible via QR code.
    """
    try:
        user = User.objects.get(gsezid=gsezid)
        return render(request, 'core/user/idcard.html', {'user': user})
    except User.DoesNotExist:
        return render(request, 'core/user/idcard_not_found.html', {'gsezid': gsezid})

@login_required
@user_passes_test(is_regular_user)
def user_job_opportunities(request):
    # In a real application, you would have a Job model
    # For now, let's simulate some job data
    jobs = [
        {
            'id': 1,
            'title': 'Software Developer',
            'company': 'Tech Solutions Ltd',
            'location': 'GSEZ Zone A',
            'description': 'Looking for experienced developers',
            'requirements': 'Python, Django, JavaScript',
            'posted_date': '2023-05-15'
        },
        {
            'id': 2,
            'title': 'Network Administrator',
            'company': 'InfoSec Inc',
            'location': 'GSEZ Zone B',
            'description': 'Managing network infrastructure',
            'requirements': 'CCNA, 3+ years experience',
            'posted_date': '2023-05-20'
        }
    ]
    
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        message = request.POST.get('message')
        
        # In a real application, you would save this to a JobApplication model
        messages.success(request, 'Your job inquiry has been submitted successfully.')
        return redirect('user_job_opportunities')
    
    return render(request, 'core/user/job_opportunities.html', {'jobs': jobs})

@login_required
@user_passes_test(is_regular_user)
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')
            
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
            
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password changed successfully. Please login again.')
        return redirect('login')
        
    return render(request, 'core/user/change_password.html')

# Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    users_count = User.objects.filter(user_type='user').count()
    companies_count = Company.objects.count()
    hr_count = User.objects.filter(user_type='hr').count()
    security_count = User.objects.filter(user_type='security').count()
    printed_users_count = User.objects.filter(user_type='user', is_printed=True).count()
    
    return render(request, 'core/admin/dashboard.html', {
        'users_count': users_count,
        'companies_count': companies_count,
        'hr_count': hr_count,
        'security_count': security_count,
        'printed_users_count': printed_users_count
    })

@login_required
@user_passes_test(is_admin)
def admin_manage_users(request):
    # Define filters
    status_filter = request.GET.get('status', None)
    verified_filter = request.GET.get('verified', None)
    printed_filter = request.GET.get('printed', None)
    search_query = request.GET.get('search', '')
    
    # Get items per page preference, default to 10
    items_per_page = request.GET.get('per_page', '10')
    if items_per_page not in ['5', '10', '15']:
        items_per_page = '10'
    
    # Start with all users of type 'user'
    users = User.objects.filter(user_type='user')
    
    # Apply filters
    if status_filter:
        users = users.filter(status=status_filter)
    
    if verified_filter:
        if verified_filter == 'yes':
            users = users.filter(is_verified=True)
        elif verified_filter == 'no':
            users = users.filter(is_verified=False)
        
    if printed_filter:
        if printed_filter == 'yes':
            users = users.filter(is_printed=True)
        elif printed_filter == 'no':
            users = users.filter(is_printed=False)
        
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(gsezid__icontains=search_query)
        )
    
    # Order users by username
    users = users.order_by('username')
    
    # Handle batch actions
    if request.method == 'POST':
        print("POST received:", request.POST)
        print("POST data keys:", list(request.POST.keys()))
        
        # Check for source field to differentiate between bulk actions and other actions
        source = request.POST.get('source', '')
        action = request.POST.get('action')
        bulk_action = request.POST.get('bulk_action')
        
        print(f"Source: {source}, Action: {action}, Bulk Action: {bulk_action}")
        
        # Handle bulk print/not print actions
        if bulk_action in ['mark_printed', 'mark_not_printed']:
            selected_users = request.POST.getlist('selected_users')
            print("Selected users for bulk action:", selected_users)
            
            if selected_users:
                is_printed = bulk_action == 'mark_printed'
                try:
                    # Log the users before update
                    before_users = list(User.objects.filter(id__in=selected_users).values('id', 'username', 'is_printed'))
                    print(f"Users before update: {before_users}")
                    
                    updated_count = User.objects.filter(id__in=selected_users).update(is_printed=is_printed)
                    
                    # Log the users after update
                    after_users = list(User.objects.filter(id__in=selected_users).values('id', 'username', 'is_printed'))
                    print(f"Users after update: {after_users}")
                    
                    action_text = "printed" if is_printed else "not printed"
                    print(f"Updated {updated_count} users to is_printed={is_printed}")
                    messages.success(request, f'{updated_count} users marked as {action_text} successfully.')
                except Exception as e:
                    print(f"Error updating is_printed: {e}")
                    messages.error(request, f'Error: {e}')
            else:
                messages.warning(request, 'No users were selected.')
            
            return redirect('admin_manage_users')
        
        # Handle delete user action (from modal)
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            if user_id:
                try:
                    user_to_delete = User.objects.get(id=user_id)
                    user_name = user_to_delete.get_full_name()
                    user_to_delete.delete()
                    messages.success(request, f'User "{user_name}" deleted successfully.')
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')
            return redirect('admin_manage_users')
    
    # Get available status choices for filtering
    status_choices = dict(User.STATUS_CHOICES)
    
    # Pagination
    paginator = Paginator(users, int(items_per_page))
    page = request.GET.get('page', 1)
    
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    
    return render(request, 'core/admin/manage_users.html', {
        'users': users_page,
        'status_choices': status_choices,
        'current_status': status_filter,
        'current_verified': verified_filter,
        'current_printed': printed_filter,
        'current_search': search_query,
        'items_per_page': items_per_page,
        'total_users': users.count(),
        'page_obj': users_page,
        'paginator': paginator
    })

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    documents = Document.objects.filter(user=user)
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('admin_user_detail', user_id=user.id)
    else:
        form = UserManagementForm(instance=user)
    
    return render(request, 'core/admin/user_detail.html', {
        'user_obj': user,
        'documents': documents,
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    try:
        user_obj = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_manage_users')
    
    # Process JSON fields for display
    emergency_contacts = user_obj.get_emergency_contacts()
    family_members = user_obj.get_family_members()
    previous_employers = user_obj.get_previous_employers() 
    qualifications = user_obj.get_qualifications()
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=user_obj)
        
        # Check if we have a camera capture image data
        camera_capture_data = request.POST.get('camera_capture_data')
        if camera_capture_data and camera_capture_data.startswith('data:image'):
            try:
                # Process the base64 image data
                format, imgstr = camera_capture_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Convert base64 to file
                import base64
                from django.core.files.base import ContentFile
                
                # Create a ContentFile from the decoded base64 data
                filename = f"{user_obj.gsezid}.{ext}" if user_obj.gsezid else f"user_{user_obj.id}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=filename)
                
                # Assign the file to the user's profile_photo field
                user_obj.profile_photo.save(filename, data, save=False)
                
                # Set the profile_full_link field with .jpg extension
                user_obj.profile_full_link = f"http://207.108.234.113:83/{user_obj.gsezid}.jpg"
                
            except Exception as e:
                print(f"Error processing camera capture data: {e}")
        elif 'profile_photo' in request.FILES:
            # If a new profile photo was uploaded via the form, update the profile_full_link with .jpg extension
            user_obj.profile_full_link = f"http://207.108.234.113:83/{user_obj.gsezid}.jpg"
        
        # Check for deleted items
        deleted_contacts = request.POST.getlist('deleted_contacts[]', [])
        deleted_family_members = request.POST.getlist('deleted_family_members[]', [])
        deleted_employers = request.POST.getlist('deleted_employers[]', [])
        deleted_qualifications = request.POST.getlist('deleted_qualifications[]', [])
        
        # Process extra items
        contact_names_extra = request.POST.getlist('emergency_contact_name_extra[]', [])
        contact_numbers_extra = request.POST.getlist('emergency_contact_number_extra[]', [])
        
        family_names_extra = request.POST.getlist('family_member_name_extra[]', [])
        family_relations_extra = request.POST.getlist('family_member_relation_extra[]', [])
        family_numbers_extra = request.POST.getlist('family_member_number_extra[]', [])
        
        employer_names_extra = request.POST.getlist('previous_employer_name_extra[]', [])
        employer_join_dates_extra = request.POST.getlist('previous_employer_join_date_extra[]', [])
        employer_leave_dates_extra = request.POST.getlist('previous_employer_leave_date_extra[]', [])
        employer_remarks_extra = request.POST.getlist('previous_employer_remarks_extra[]', [])
        employer_ratings_extra = request.POST.getlist('previous_employer_rating_extra[]', [])
        
        qualification_names_extra = request.POST.getlist('qualification_extra[]', [])
        institution_names_extra = request.POST.getlist('institution_extra[]', [])
        year_of_passings_extra = request.POST.getlist('year_of_passing_extra[]', [])
        
        # Check allow_login status
        allow_login = request.POST.get('allow_login') == 'true'
        
        # Check for password change
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        if form.is_valid():
            user = form.save(commit=False)
            
            # Set is_active based on allow_login
            user.is_active = allow_login
            
            # Set new password if provided
            if password1 and password2 and password1 == password2:
                user.set_password(password1)
            elif password1 or password2:  # Only one password field is filled
                messages.warning(request, 'Both password fields must match to change password. Password not updated.')
            
            # Process emergency contacts
            if deleted_contacts:
                updated_contacts = []
                for i, contact in enumerate(emergency_contacts):
                    if str(i) not in deleted_contacts:
                        updated_contacts.append(contact)
                user.set_emergency_contacts(updated_contacts)
            
            # Add extra emergency contacts
            for i in range(len(contact_names_extra)):
                if contact_names_extra[i] and contact_numbers_extra[i]:
                    emergency_contacts = user.get_emergency_contacts()
                    emergency_contacts.append({
                        'name': contact_names_extra[i],
                        'number': contact_numbers_extra[i]
                    })
                    user.set_emergency_contacts(emergency_contacts)
            
            # Process family members
            if deleted_family_members:
                updated_members = []
                for i, member in enumerate(family_members):
                    if str(i) not in deleted_family_members:
                        updated_members.append(member)
                user.set_family_members(updated_members)
            
            # Process previous employers
            if deleted_employers:
                updated_employers = []
                for i, employer in enumerate(previous_employers):
                    if str(i) not in deleted_employers:
                        updated_employers.append(employer)
                user.set_previous_employers(updated_employers)
            
            # Add extra previous employers
            for i in range(len(employer_names_extra)):
                if employer_names_extra[i]:
                    previous_employers = user.get_previous_employers()
                    previous_employers.append({
                        'company': employer_names_extra[i],
                        'join_date': employer_join_dates_extra[i] if i < len(employer_join_dates_extra) else '',
                        'leave_date': employer_leave_dates_extra[i] if i < len(employer_leave_dates_extra) else '',
                        'remarks': employer_remarks_extra[i] if i < len(employer_remarks_extra) else '',
                        'rating': employer_ratings_extra[i] if i < len(employer_ratings_extra) else ''
                    })
                    user.set_previous_employers(previous_employers)
            
            # Process qualifications
            if deleted_qualifications:
                updated_qualifications = []
                for i, qualification in enumerate(qualifications):
                    if str(i) not in deleted_qualifications:
                        updated_qualifications.append(qualification)
                user.set_qualifications(updated_qualifications)
            
            # Add extra qualifications
            for i in range(len(qualification_names_extra)):
                if qualification_names_extra[i] and institution_names_extra[i]:
                    qualifications = user.get_qualifications()
                    qualifications.append({
                        'qualification': qualification_names_extra[i],
                        'institution': institution_names_extra[i] if i < len(institution_names_extra) else '',
                        'year': year_of_passings_extra[i] if i < len(year_of_passings_extra) else ''
                    })
                    user.set_qualifications(qualifications)
            
            user.save()
            
            password_msg = " Password was updated." if password1 and password2 and password1 == password2 else ""
            login_status = "with login access" if allow_login else "without login access"
            messages.success(request, f'User updated successfully {login_status}.{password_msg}')
            return redirect('admin_manage_users')
    else:
        form = AdminUserEditForm(instance=user_obj)
    
    # Get existing data for display
    emergency_contacts = user_obj.get_emergency_contacts()
    family_members = user_obj.get_family_members()
    previous_employers = user_obj.get_previous_employers()
    qualifications = user_obj.get_qualifications()
    
    return render(request, 'core/admin/edit_user.html', {
        'user_obj': user_obj,
        'form': form,
        'emergency_contacts': emergency_contacts,
        'family_members': family_members,
        'previous_employers': previous_employers,
        'qualifications': qualifications
    })

@login_required
@user_passes_test(is_admin)
def admin_create_user(request):
    # Generate next GSEZ ID using the new format
    next_gsez_id = generate_gsezid()
    
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST, request.FILES)
        
        # Check if we have a camera capture image data
        camera_capture_data = request.POST.get('camera_capture_data')
        
        # Check allow_login status
        allow_login = request.POST.get('allow_login') == 'true'
        
        # If login is not allowed, we'll generate a random password later
        if not allow_login:
            # Create a copy of POST data to modify
            post_data = request.POST.copy()
            # Generate a random password that meets Django's requirements
            import random
            import string
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + '!@#'
            post_data['password1'] = random_password
            post_data['password2'] = random_password
            # Update the form with modified data
            form = AdminUserCreationForm(post_data, request.FILES)
        
        if form.is_valid():
            user = form.save(commit=False)
            # User type is already handled in the form, but we'll leave this line for safety
            user.user_type = request.POST.get('user_type', 'user')
            
            # If no GSEZ ID provided, use the auto-generated one
            if not user.gsezid:
                user.gsezid = next_gsez_id
            
            # If login is not allowed, store this information
            user.is_active = allow_login
                
            # Save the user first to get an ID
            user.save()
            
            # Process camera capture if available
            if camera_capture_data and camera_capture_data.startswith('data:image'):
                try:
                    # Process the base64 image data
                    format, imgstr = camera_capture_data.split(';base64,')
                    ext = format.split('/')[-1]
                    
                    # Convert base64 to file
                    import base64
                    from django.core.files.base import ContentFile
                    
                    # Create a ContentFile from the decoded base64 data
                    filename = f"{user.gsezid}.{ext}"
                    data = ContentFile(base64.b64decode(imgstr), name=filename)
                    
                    # Assign the file to the user's profile_photo field
                    user.profile_photo.save(filename, data, save=False)
                    
                    # Always set the profile_full_link with .jpg extension
                    user.profile_full_link = f"http://207.108.234.113:83/{user.gsezid}.jpg"
                    
                except Exception as e:
                    print(f"Error processing camera capture data: {e}")
            elif user.profile_photo:
                # If a profile photo was uploaded via the form, set the profile_full_link with .jpg extension
                user.profile_full_link = f"http://207.108.234.113:83/{user.gsezid}.jpg"
            
            # Process additional emergency contacts
            extra_names = request.POST.getlist('emergency_contact_name_extra[]')
            extra_numbers = request.POST.getlist('emergency_contact_number_extra[]')
            
            if extra_names and extra_numbers:
                emergency_contacts = user.get_emergency_contacts()
                for i in range(len(extra_names)):
                    if i < len(extra_numbers) and extra_names[i].strip():
                        emergency_contacts.append({
                            'name': extra_names[i],
                            'number': extra_numbers[i]
                        })
                user.set_emergency_contacts(emergency_contacts)
            
            # Process additional family members
            extra_names = request.POST.getlist('family_member_name_extra[]')
            extra_relations = request.POST.getlist('family_member_relation_extra[]')
            extra_numbers = request.POST.getlist('family_member_number_extra[]')
            
            if extra_names and extra_relations:
                family_members = user.get_family_members()
                for i in range(len(extra_names)):
                    if i < len(extra_relations) and extra_names[i].strip():
                        number = extra_numbers[i] if i < len(extra_numbers) else ''
                        family_members.append({
                            'name': extra_names[i],
                            'relation': extra_relations[i],
                            'number': number
                        })
                user.set_family_members(family_members)
            
            # Process additional previous employers
            extra_companies = request.POST.getlist('previous_employer_name_extra[]')
            extra_join_dates = request.POST.getlist('previous_employer_join_date_extra[]')
            extra_leave_dates = request.POST.getlist('previous_employer_leave_date_extra[]')
            extra_remarks = request.POST.getlist('previous_employer_remarks_extra[]')
            extra_ratings = request.POST.getlist('previous_employer_rating_extra[]')
            
            if extra_companies:
                previous_employers = user.get_previous_employers()
                for i in range(len(extra_companies)):
                    if extra_companies[i].strip():
                        join_date = extra_join_dates[i] if i < len(extra_join_dates) else None
                        leave_date = extra_leave_dates[i] if i < len(extra_leave_dates) else None
                        remarks = extra_remarks[i] if i < len(extra_remarks) else ''
                        rating = extra_ratings[i] if i < len(extra_ratings) and extra_ratings[i].strip() else 0
                        
                        # Convert date objects to strings to make them JSON serializable
                        if join_date:
                            join_date = join_date if isinstance(join_date, str) else join_date.strftime('%Y-%m-%d')
                        if leave_date:
                            leave_date = leave_date if isinstance(leave_date, str) else leave_date.strftime('%Y-%m-%d')
                        
                        previous_employers.append({
                            'company': extra_companies[i],
                            'join_date': join_date,
                            'leave_date': leave_date,
                            'remarks': remarks,
                            'rating': rating
                        })
                user.set_previous_employers(previous_employers)
            
            # Process additional qualifications
            extra_quals = request.POST.getlist('qualification_extra[]')
            extra_insts = request.POST.getlist('institution_extra[]')
            extra_years = request.POST.getlist('year_of_passing_extra[]')
            
            if extra_quals and extra_insts:
                qualifications = user.get_qualifications()
                for i in range(len(extra_quals)):
                    if i < len(extra_insts) and extra_quals[i].strip():
                        year = extra_years[i] if i < len(extra_years) else ''
                        qualifications.append({
                            'qualification': extra_quals[i],
                            'institution': extra_insts[i],
                            'year': year
                        })
                user.set_qualifications(qualifications)
            
            # Save the user with all the additional data
            user.save()
            
            login_status = "with login access" if allow_login else "without login access"
            messages.success(request, f'User created successfully {login_status}.')
            return redirect('admin_manage_users')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'core/admin/create_user.html', {
        'form': form,
        'next_gsez_id': next_gsez_id
    })

@login_required
@user_passes_test(is_admin)
def admin_manage_companies(request):
    # Get items per page parameter for compatibility
    items_per_page = request.GET.get('per_page', '10')
    if items_per_page not in ['5', '10', '15']:
        items_per_page = '10'
    
    # Handle POST requests (add, edit, delete)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Handle edit action
        if action == 'edit':
            company_id = request.POST.get('company_id')
            company_name = request.POST.get('company_name')
            
            try:
                company = Company.objects.get(id=company_id)
                company.company_name = company_name
                company.save()
                messages.success(request, 'Company updated successfully.')
            except Company.DoesNotExist:
                messages.error(request, 'Company not found.')
            
            return redirect('admin_manage_companies')
        
        # Handle delete action
        elif action == 'delete':
            company_id = request.POST.get('company_id')
            
            try:
                company = Company.objects.get(id=company_id)
                company.delete()
                messages.success(request, 'Company deleted successfully.')
            except Company.DoesNotExist:
                messages.error(request, 'Company not found.')
            
            return redirect('admin_manage_companies')
        
        # Handle add action (default)
        else:
            form = CompanyForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Company added successfully.')
                return redirect('admin_manage_companies')
    else:
        form = CompanyForm()
    
    # Get all companies
    companies = Company.objects.all().order_by('id')
    
    # Pagination
    paginator = Paginator(companies, int(items_per_page))
    page = request.GET.get('page', 1)
    
    try:
        companies_page = paginator.page(page)
    except PageNotAnInteger:
        companies_page = paginator.page(1)
    except EmptyPage:
        companies_page = paginator.page(paginator.num_pages)
    
    return render(request, 'core/admin/manage_companies.html', {
        'companies': companies_page,
        'total_items': companies.count(),
        'items_per_page': items_per_page,
        'form': form,
        'page_obj': companies_page,
        'paginator': paginator
    })

@login_required
@user_passes_test(is_admin)
def admin_manage_hr(request):
    # Get items per page parameter for compatibility
    items_per_page = request.GET.get('per_page', '10')
    if items_per_page not in ['5', '10', '15']:
        items_per_page = '10'
    
    # Get all HR staff
    hrs = User.objects.filter(user_type='hr').order_by('id')
    companies = Company.objects.all()
    
    if request.method == 'POST':
        # Check for delete action first
        if request.POST.get('action') == 'delete':
            hr_id = request.POST.get('hr_id')
            try:
                hr_user = User.objects.get(id=hr_id)
                hr_user.delete()
                messages.success(request, 'HR staff deleted successfully.')
            except User.DoesNotExist:
                messages.error(request, 'HR staff not found.')
            return redirect('admin_manage_hr')
            
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'hr'
            
            # Generate GSEZ ID if not provided, which will be used as username
            if not user.gsezid:
                user.gsezid = generate_gsezid()
            
            # Set username to gsezid to prevent NOT NULL constraint error
            user.username = user.gsezid
            
            user.save()
            
            # Assign company
            company_id = request.POST.get('company')
            if company_id:
                try:
                    company = Company.objects.get(id=company_id)
                    user.current_employer_company = company
                    user.save()
                except Company.DoesNotExist:
                    messages.warning(request, f'Company with ID {company_id} not found.')
                
            messages.success(request, 'HR created successfully.')
            return redirect('admin_manage_hr')
    else:
        form = UserRegistrationForm()
    
    # Pagination
    paginator = Paginator(hrs, int(items_per_page))
    page = request.GET.get('page', 1)
    
    try:
        hrs_page = paginator.page(page)
    except PageNotAnInteger:
        hrs_page = paginator.page(1)
    except EmptyPage:
        hrs_page = paginator.page(paginator.num_pages)
    
    return render(request, 'core/admin/manage_hr.html', {
        'hrs': hrs_page,
        'total_items': hrs.count(),
        'items_per_page': items_per_page,
        'companies': companies,
        'form': form,
        'page_obj': hrs_page,
        'paginator': paginator
    })

@login_required
@user_passes_test(is_admin)
def admin_manage_security(request):
    # Get items per page parameter for compatibility
    items_per_page = request.GET.get('per_page', '10')
    if items_per_page not in ['5', '10', '15']:
        items_per_page = '10'
    
    # Get all security staff
    security_staff = User.objects.filter(user_type='security').order_by('id')
    
    if request.method == 'POST':
        # Check for delete action first
        if request.POST.get('action') == 'delete':
            security_id = request.POST.get('security_id')
            try:
                security_user = User.objects.get(id=security_id)
                security_user.delete()
                messages.success(request, 'Security staff deleted successfully.')
            except User.DoesNotExist:
                messages.error(request, 'Security staff not found.')
            return redirect('admin_manage_security')
        
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'security'
            
            # Generate GSEZ ID if not provided, which will be used as username
            if not user.gsezid:
                user.gsezid = generate_gsezid()
            
            # Set username to gsezid to prevent NOT NULL constraint error
            user.username = user.gsezid
            
            user.save()
            messages.success(request, 'Security staff created successfully.')
            return redirect('admin_manage_security')
    else:
        form = UserRegistrationForm()
    
    # Pagination
    paginator = Paginator(security_staff, int(items_per_page))
    page = request.GET.get('page', 1)
    
    try:
        security_staff_page = paginator.page(page)
    except PageNotAnInteger:
        security_staff_page = paginator.page(1)
    except EmptyPage:
        security_staff_page = paginator.page(paginator.num_pages)
    
    return render(request, 'core/admin/manage_security.html', {
        'security_staff': security_staff_page,
        'total_items': security_staff.count(),
        'items_per_page': items_per_page,
        'form': form,
        'page_obj': security_staff_page,
        'paginator': paginator
    })

@login_required
@user_passes_test(is_admin)
def admin_export_users(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')
    
    # Sheet header, first row
    row_num = 0
    
    columns = [
        'ID', 'Username', 'Email', 'First Name', 'Middle Name', 'Last Name',
        'User Type', 'Status', 'Is Verified', 'Is Profile Complete', 'Is Printed',
        'Nationality', 'Date of Birth', 'GSEZ Card Issue Date', 'GSEZ Card Expiry Date', 'GSEZ ID',
        'Profile Full Link', 'Current Address', 'Is Permanent', 'Permanent Address',
        'Current Employer', 'Join Date', 'Employee Code', 'Designation', 'Department', 'Company',
        'Remarks', 'Rating', 'Emergency Contacts', 'Family Members', 'Previous Employers', 'Qualifications'
    ]
    
    # Write header row
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title)
    
    # Get all users
    users = User.objects.filter(user_type='user')
    
    # Write data rows
    for user in users:
        row_num += 1
        row = [
            user.id,
            user.username,
            user.email,
            user.first_name,
            user.middle_name if user.middle_name else '',
            user.last_name,
            user.user_type,
            user.status,
            '1' if user.is_verified else '0',
            '1' if not user.is_required_profile_detail else '0',
            '1' if user.is_printed else '0',
            user.nationality if user.nationality else '',
            str(user.date_of_birth) if user.date_of_birth else '',
            str(user.gsez_card_issue_date) if user.gsez_card_issue_date else '',
            str(user.gsez_card_expiry_date) if user.gsez_card_expiry_date else '',
            user.gsezid if user.gsezid else '',
            user.profile_full_link if user.profile_full_link else '',
            user.current_address if user.current_address else '',
            '1' if user.is_permanent else '0',
            user.permanent_address if user.permanent_address else '',
            user.current_employer,
            str(user.current_employer_join_date) if user.current_employer_join_date else '',
            user.current_employer_emp_code,
            user.current_employer_designation,
            user.current_employer_department,
            user.current_employer_company.company_name if user.current_employer_company else '',
            user.current_employer_remarks,
            str(user.current_employer_rating) if user.current_employer_rating else '',
            user.emergency_contact_numbers,
            user.family_members,
            user.previous_employers,
            user.qualifications
        ]
        
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, str(cell_value) if cell_value is not None else '')
    
    wb.save(response)
    return response

@login_required
@user_passes_test(is_admin)
def admin_export_users_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_template.csv"'
    
    writer = csv.writer(response)
    
    # Header row with all User model fields
    headers = [
        'username', 'password', 'first_name', 'middle_name', 'last_name', 'email', 
        'user_type', 'status', 'is_verified', 'is_required_profile_detail', 'is_printed',
        'nationality', 'date_of_birth', 'gsez_card_issue_date', 'gsez_card_expiry_date', 'gsezid',
        'profile_full_link', 'current_address', 'is_permanent', 'permanent_address', 
        'current_employer', 'current_employer_join_date', 'current_employer_emp_code', 
        'current_employer_designation', 'current_employer_department', 'current_employer_company',
        'current_employer_remarks', 'current_employer_rating',
        # Split JSON fields into separate columns
        'emergency_contact_name', 'emergency_contact_number',
        'family_member_name', 'family_member_relation', 'family_member_number',
        'previous_employer_name', 'previous_employer_join_date', 'previous_employer_leave_date', 'previous_employer_remarks', 'previous_employer_rating',
        'qualification_name', 'qualification_institution', 'qualification_year'
    ]
    writer.writerow(headers)
    
    # Helpful comments row (field requirements)
    comments = [
        'Required', 'Required', 'Required', 'Optional', 'Required', 'Required',
        'Use: user/admin/hr/security', 'Use: active/inactive/blocked/terminated/under_surveillance', 
        'Use: 1/0', 'Use: 1/0', 'Use: 1/0',
        'Optional', 'Use: YYYY-MM-DD or DD/MM/YYYY', 'Use: YYYY-MM-DD or DD/MM/YYYY', 
        'Use: YYYY-MM-DD or DD/MM/YYYY', 'Optional (auto-generated if blank)',
        'Optional (e.g. http://207.108.234.113:83/GSEZID.jpg)', 'Optional', 'Use: 1/0', 'Optional',
        'Optional', 'Use: YYYY-MM-DD or DD/MM/YYYY', 'Optional', 
        'Optional', 'Optional', 'Must exist in system',
        'Optional', 'Optional (number 1-5)',
        # Comments for separated JSON fields
        'Optional', 'Optional',
        'Optional', 'Optional', 'Optional',
        'Optional', 'Use: YYYY-MM-DD or DD/MM/YYYY', 'Use: YYYY-MM-DD or DD/MM/YYYY', 'Optional', 'Optional (number 1-5)',
        'Optional', 'Optional', 'Optional (year)'
    ]
    writer.writerow(comments)
    
    # Example row 1
    example1 = [
        'john_doe', 'password123', 'John', '', 'Doe', 'john@example.com',
        'user', 'active', '1', '1', '0',
        'Indian', '1990-01-01', '2023-01-01', '2025-01-01', '',
        'http://207.108.234.113:83/ZIS2506000001.jpg', '123 Street, City', '0', '456 Street, City',
        'ACME Corp', '2022-01-01', 'EMP123', 
        'Developer', 'IT', 'Company Name',
        'Good employee', '4',
        # Separated JSON fields
        'Emergency Contact', '9876543210',
        'Jane Doe', 'Spouse', '1234567890',
        'Previous Corp', '2019-01-01', '2021-12-31', 'Worked as Developer', '3',
        'B.Tech', 'University', '2018'
    ]
    writer.writerow(example1)
    
    # Example row 2 with different date formats
    example2 = [
        'jane_smith', 'pass456', 'Jane', 'M', 'Smith', 'jane@example.com',
        'user', 'active', '0', '1', '0',
        'American', '31/05/1992', '01.02.2023', '01-02-2025', '',
        'http://207.108.234.113:83/ZIS2506000002.jpg', '789 Road, Town', '1', '789 Road, Town',
        'XYZ Ltd', '01/06/2021', 'XYZ456', 
        'Manager', 'HR', 'XYZ Company',
        'Excellent manager', '5',
        # Separated JSON fields
        'Emergency', '1234567890',
        'John Smith', 'Husband', '9876543210',
        'ABC Inc', '2018-01-01', '2021-05-31', 'Team Leader', '4',
        'MBA', 'Business School', '2016'
    ]
    writer.writerow(example2)
    
    return response

@login_required
@user_passes_test(is_admin)
def admin_import_users(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('admin_import_users')

        try:
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            headers = next(reader)  # Get header row
            next(reader, None)  # Skip the second row (instructions/comments)
            
            # Create field mapping based on headers
            field_indices = {}
            for i, header in enumerate(headers):
                # Normalize header: trim whitespace, convert to lowercase
                normalized_header = header.strip().lower()
                field_indices[normalized_header] = i
            
            # Debug field indices to help troubleshoot
            missing_required_fields = []
            required_fields = ['username', 'password', 'first_name', 'last_name', 'email']
            for field in required_fields:
                if field not in field_indices:
                    missing_required_fields.append(field)
            
            if missing_required_fields:
                messages.error(request, f"Required fields missing in CSV header: {', '.join(missing_required_fields)}")
                messages.warning(request, f"CSV headers found: {', '.join(headers)}")
                return redirect('admin_import_users')
            
            success_count = 0
            error_count = 0
            error_details = []
            
            for row_num, row in enumerate(reader, start=3):  # Start at 3 to account for header and instruction rows
                if not row or len(row) < 5:  # Skip empty rows or rows with insufficient data
                    error_details.append(f"Row {row_num}: Insufficient data (fewer than 5 columns)")
                    error_count += 1
                    continue
                
                try:
                    # Extract basic required fields
                    username = row[field_indices['username']].strip() if field_indices['username'] < len(row) else ''
                    password = row[field_indices['password']].strip() if field_indices['password'] < len(row) else ''
                    first_name = row[field_indices['first_name']].strip() if field_indices['first_name'] < len(row) else ''
                    last_name = row[field_indices['last_name']].strip() if field_indices['last_name'] < len(row) else ''
                    email = row[field_indices['email']].strip() if field_indices['email'] < len(row) else ''
                    
                    # Check if required fields are present
                    missing_fields = []
                    if not username: missing_fields.append('username')
                    if not password: missing_fields.append('password')
                    if not first_name: missing_fields.append('first_name')
                    if not last_name: missing_fields.append('last_name') 
                    if not email: missing_fields.append('email')
                    
                    if missing_fields:
                        error_details.append(f"Row {row_num}: Missing required fields: {', '.join(missing_fields)}")
                        error_count += 1
                        continue
                    
                    # Check if user already exists
                    if User.objects.filter(username=username).exists():
                        error_details.append(f"Row {row_num}: User with username '{username}' already exists")
                        error_count += 1
                        continue
                    
                    # Create user with basic fields
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    # Set user type and status explicitly first
                    if 'user_type' in field_indices and field_indices['user_type'] < len(row):
                        user_type_value = row[field_indices['user_type']].strip()
                        if user_type_value in [choice[0] for choice in User.USER_TYPE_CHOICES]:
                            user.user_type = user_type_value
                        elif user_type_value:
                            error_details.append(f"Row {row_num}: Invalid user_type: {user_type_value}. Using default.")
                    
                    if 'status' in field_indices and field_indices['status'] < len(row):
                        status_value = row[field_indices['status']].strip()
                        if status_value in [choice[0] for choice in User.STATUS_CHOICES]:
                            user.status = status_value
                        elif status_value:
                            error_details.append(f"Row {row_num}: Invalid status: {status_value}. Using default.")
                    
                    # Set optional text fields
                    optional_text_fields = [
                        'middle_name', 'nationality', 'gsezid', 'current_address',
                        'permanent_address', 'current_employer', 'current_employer_emp_code',
                        'current_employer_designation', 'current_employer_department',
                        'current_employer_remarks', 'profile_full_link'
                    ]
                    
                    for field in optional_text_fields:
                        if field in field_indices and field_indices[field] < len(row):
                            value = row[field_indices[field]].strip()
                            if value:
                                setattr(user, field, value)
                    
                    # Set boolean fields
                    boolean_fields = [
                        'is_verified', 'is_required_profile_detail', 'is_printed', 'is_permanent'
                    ]
                    
                    for field in boolean_fields:
                        if field in field_indices and field_indices[field] < len(row):
                            value = row[field_indices[field]].strip().lower()
                            setattr(user, field, value in ['1', 'true', 'yes'])
                    
                    # Set date fields
                    date_fields = [
                        'date_of_birth', 'gsez_card_issue_date', 'gsez_card_expiry_date',
                        'current_employer_join_date'
                    ]
                    
                    date_field_values = {}  # Store processed date values for final debug message
                    for field in date_fields:
                        if field in field_indices and field_indices[field] < len(row):
                            value = row[field_indices[field]].strip()
                            if value:
                                try:
                                    # Try different date formats
                                    date_value = None
                                    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%d.%m.%Y']
                                    
                                    for date_format in date_formats:
                                        try:
                                            date_value = datetime.strptime(value, date_format).date()
                                            # Store the format that worked
                                            date_field_values[field] = {
                                                'raw': value,
                                                'parsed': str(date_value),
                                                'format_used': date_format
                                            }
                                            break
                                        except ValueError:
                                            continue
                                    
                                    if date_value:
                                        setattr(user, field, date_value)
                                    else:
                                        error_details.append(f"Row {row_num}: Invalid date format for {field}: {value}. Expected YYYY-MM-DD or DD/MM/YYYY")
                                except Exception as e:
                                    error_details.append(f"Row {row_num}: Error processing date {field}: {str(e)}")
                                    # Continue with other fields even if this date field fails
                    
                    # Remove the debug message - we don't want it to show in the UI
                    # (The debug info is still collected in date_field_values if needed later)
                    
                    # Set integer fields
                    if 'current_employer_rating' in field_indices and field_indices['current_employer_rating'] < len(row):
                        try:
                            rating_value = row[field_indices['current_employer_rating']].strip()
                            if rating_value:
                                rating = int(rating_value)
                                user.current_employer_rating = rating
                        except ValueError:
                            error_details.append(f"Row {row_num}: Invalid rating value: {rating_value}. Expected integer")
                    
                    # Set company foreign key
                    if 'current_employer_company' in field_indices and field_indices['current_employer_company'] < len(row):
                        company_name = row[field_indices['current_employer_company']].strip()
                        if company_name:
                            try:
                                company, created = Company.objects.get_or_create(company_name=company_name)
                                user.current_employer_company = company
                            except Exception as e:
                                error_details.append(f"Row {row_num}: Error setting company: {str(e)}")
                    
                    # Process emergency contacts (comma-separated fields)
                    emergency_contacts = []
                    if 'emergency_contact_name' in field_indices and 'emergency_contact_number' in field_indices:
                        name = row[field_indices['emergency_contact_name']].strip() if field_indices['emergency_contact_name'] < len(row) else ''
                        number = row[field_indices['emergency_contact_number']].strip() if field_indices['emergency_contact_number'] < len(row) else ''
                        
                        if name and number:
                            emergency_contacts.append({
                                'name': name,
                                'number': number
                            })
                            user.emergency_contact_numbers = json.dumps(emergency_contacts)
                    # Also support the old JSON format for backward compatibility
                    elif 'emergency_contact_numbers' in field_indices and field_indices['emergency_contact_numbers'] < len(row):
                        value = row[field_indices['emergency_contact_numbers']].strip()
                        if value:
                            try:
                                # Try to parse JSON
                                json_value = json.loads(value)
                                user.emergency_contact_numbers = value
                            except json.JSONDecodeError as je:
                                error_details.append(f"Row {row_num}: Invalid JSON format for emergency_contact_numbers: {str(je)}")
                    
                    # Process family members (comma-separated fields)
                    family_members = []
                    if all(field in field_indices for field in ['family_member_name', 'family_member_relation']):
                        name = row[field_indices['family_member_name']].strip() if field_indices['family_member_name'] < len(row) else ''
                        relation = row[field_indices['family_member_relation']].strip() if field_indices['family_member_relation'] < len(row) else ''
                        number = ''
                        
                        if 'family_member_number' in field_indices and field_indices['family_member_number'] < len(row):
                            number = row[field_indices['family_member_number']].strip()
                        
                        if name and relation:
                            family_members.append({
                                'name': name,
                                'relation': relation,
                                'number': number
                            })
                            user.family_members = json.dumps(family_members)
                    # Also support the old JSON format for backward compatibility
                    elif 'family_members' in field_indices and field_indices['family_members'] < len(row):
                        value = row[field_indices['family_members']].strip()
                        if value:
                            try:
                                # Try to parse JSON
                                json_value = json.loads(value)
                                user.family_members = value
                            except json.JSONDecodeError as je:
                                error_details.append(f"Row {row_num}: Invalid JSON format for family_members: {str(je)}")
                    
                    # Process previous employers (comma-separated fields)
                    previous_employers = []
                    if 'previous_employer_name' in field_indices:
                        company = row[field_indices['previous_employer_name']].strip() if field_indices['previous_employer_name'] < len(row) else ''
                        
                        if company:
                            employer_data = {'company': company}
                            
                            # Add optional fields if they exist
                            for field_pair in [
                                ('previous_employer_join_date', 'join_date'),
                                ('previous_employer_leave_date', 'leave_date'),
                                ('previous_employer_remarks', 'remarks'),
                                ('previous_employer_rating', 'rating')
                            ]:
                                csv_field, json_field = field_pair
                                if csv_field in field_indices and field_indices[csv_field] < len(row):
                                    value = row[field_indices[csv_field]].strip()
                                    if value:
                                        employer_data[json_field] = value
                            
                            previous_employers.append(employer_data)
                            user.previous_employers = json.dumps(previous_employers)
                    # Also support the old JSON format for backward compatibility
                    elif 'previous_employers' in field_indices and field_indices['previous_employers'] < len(row):
                        value = row[field_indices['previous_employers']].strip()
                        if value:
                            try:
                                # Try to parse JSON
                                json_value = json.loads(value)
                                user.previous_employers = value
                            except json.JSONDecodeError as je:
                                error_details.append(f"Row {row_num}: Invalid JSON format for previous_employers: {str(je)}")
                    
                    # Process qualifications (comma-separated fields)
                    qualifications = []
                    if 'qualification_name' in field_indices and 'qualification_institution' in field_indices:
                        qualification = row[field_indices['qualification_name']].strip() if field_indices['qualification_name'] < len(row) else ''
                        institution = row[field_indices['qualification_institution']].strip() if field_indices['qualification_institution'] < len(row) else ''
                        
                        if qualification and institution:
                            qual_data = {
                                'qualification': qualification,
                                'institution': institution
                            }
                            
                            # Add year if it exists
                            if 'qualification_year' in field_indices and field_indices['qualification_year'] < len(row):
                                year = row[field_indices['qualification_year']].strip()
                                if year:
                                    qual_data['year'] = year
                            
                            qualifications.append(qual_data)
                            user.qualifications = json.dumps(qualifications)
                    # Also support the old JSON format for backward compatibility
                    elif 'qualifications' in field_indices and field_indices['qualifications'] < len(row):
                        value = row[field_indices['qualifications']].strip()
                        if value:
                            try:
                                # Try to parse JSON
                                json_value = json.loads(value)
                                user.qualifications = value
                            except json.JSONDecodeError as je:
                                error_details.append(f"Row {row_num}: Invalid JSON format for qualifications: {str(je)}")
                    
                    # Generate GSEZ ID if not provided
                    if not user.gsezid:
                        user.gsezid = generate_gsezid()
                    
                    # Save the user
                    user.save()
                    success_count += 1
                    
                except Exception as e:
                    error_details.append(f"Row {row_num}: Unexpected error: {str(e)}")
                    error_count += 1
            
            # Display success and errors
            if success_count > 0:
                messages.success(request, f'{success_count} users imported successfully.')
            else:
                messages.warning(request, "No users were imported.")
                
            if error_count > 0:
                messages.error(request, f'{error_count} users skipped due to errors.')
                # Only show detailed errors if import completely failed
                if success_count == 0 and error_details:
                    # Show the first few errors (limit to avoid too many messages)
                    for i, error in enumerate(error_details[:3]):
                        messages.warning(request, error)
                    if len(error_details) > 3:
                        messages.warning(request, f"... and {len(error_details) - 3} more errors.")
                
        except Exception as e:
            messages.error(request, f'Error importing users: {str(e)}')
        
        return redirect('admin_manage_users')
    
    return render(request, 'core/admin/import_users.html')

@login_required
@user_passes_test(is_admin)
def admin_export_companies(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="companies.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Company'])  # Simplified header
    
    companies = Company.objects.all().values_list('company_name')
    for company in companies:
        writer.writerow(company)
    
    return response

@login_required
@user_passes_test(is_admin)
def admin_import_companies(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('admin_manage_companies')

        try:
            # Read csv file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            next(reader)  # Skip header row

            success_count = 0
            error_count = 0
            
            # Process each row - expecting only company name in each row
            for row in reader:
                if not row:  # Skip empty rows
                    continue
                
                company_name = row[0].strip()
                if company_name:
                    try:
                        # Check if company already exists
                        existing_company = Company.objects.filter(company_name=company_name).exists()
                        if not existing_company:
                            Company.objects.create(company_name=company_name)
                            success_count += 1
                        else:
                            error_count += 1  # Company already exists
                    except Exception as e:
                        error_count += 1
            
            messages.success(request, f'{success_count} companies imported successfully. {error_count} companies skipped (already exist or invalid data).')
        except Exception as e:
            messages.error(request, f'Error importing companies: {str(e)}')
        
        return redirect('admin_manage_companies')
    
    return render(request, 'core/admin/import_companies.html')

@login_required
@user_passes_test(is_admin)
def admin_manage_documents(request):
    documents = Document.objects.all().order_by('-id')
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        documents = documents.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(govt_id_number__icontains=search_query)
        )
    
    # Get items per page preference for compatibility
    items_per_page = request.GET.get('per_page', '10')
    if items_per_page not in ['5', '10', '15']:
        items_per_page = '10'
    
    # Pagination
    paginator = Paginator(documents, int(items_per_page))
    page = request.GET.get('page', 1)
    
    try:
        documents_page = paginator.page(page)
    except PageNotAnInteger:
        documents_page = paginator.page(1)
    except EmptyPage:
        documents_page = paginator.page(paginator.num_pages)
    
    return render(request, 'core/admin/manage_documents.html', {
        'documents': documents_page,
        'search_query': search_query,
        'items_per_page': items_per_page,
        'total_items': documents.count(),
        'page_obj': documents_page,
        'paginator': paginator
    })

@login_required
@user_passes_test(is_admin)
def admin_create_document(request, user_id=None):
    user = None
    if user_id:
        user = get_object_or_404(User, id=user_id)
    
    # Get all users for dropdown
    users = User.objects.filter(user_type='user')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        selected_user_id = request.POST.get('user')
        
        if not selected_user_id:
            messages.error(request, 'Please select a user for this document.')
            return render(request, 'core/admin/create_document.html', {'form': form, 'users': users, 'selected_user': user})
        
        if form.is_valid():
            document = form.save(commit=False)
            document.user_id = selected_user_id
            document.save()
            messages.success(request, 'Document created successfully.')
            return redirect('admin_manage_documents')
    else:
        form = DocumentForm()
    
    return render(request, 'core/admin/create_document.html', {
        'form': form, 
        'users': users,
        'selected_user': user
    })

@login_required
@user_passes_test(is_admin)
def admin_edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document updated successfully.')
            return redirect('admin_manage_documents')
    else:
        form = DocumentForm(instance=document)
    
    return render(request, 'core/admin/edit_document.html', {
        'form': form,
        'document': document
    })

@login_required
@user_passes_test(is_admin)
def admin_delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'GET' or request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully.')
        return redirect('admin_manage_documents')

@login_required
def user_documents(request):
    if request.user.user_type == 'admin':
        return redirect('admin_manage_documents')
    
    # For regular users, show only their documents
    documents = Document.objects.filter(user=request.user)
    
    return render(request, 'core/user/documents.html', {
        'documents': documents
    })

# HR Dashboard
@login_required
@user_passes_test(is_hr)
def hr_dashboard(request):
    company = request.user.current_employer_company
    users_in_company = User.objects.filter(current_employer_company=company).count() if company else 0
    
    return render(request, 'core/hr/dashboard.html', {
        'company': company,
        'users_count': users_in_company
    })

@login_required
@user_passes_test(is_hr)
def hr_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        
        # Check if we have a camera capture image data
        camera_capture_data = request.POST.get('camera_capture_data')
        if camera_capture_data and camera_capture_data.startswith('data:image'):
            try:
                # Process the base64 image data
                format, imgstr = camera_capture_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Convert base64 to file
                import base64
                from django.core.files.base import ContentFile
                
                # Create a ContentFile from the decoded base64 data
                filename = f"{request.user.gsezid}.{ext}" if request.user.gsezid else f"user_{request.user.id}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=filename)
                
                # Assign the file to the user's profile_photo field
                request.user.profile_photo.save(filename, data, save=False)
            except Exception as e:
                print(f"Error processing camera capture data: {e}")
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('hr_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/hr/profile.html', {'form': form})

@login_required
@user_passes_test(is_hr)
def hr_manage_company(request):
    company = request.user.current_employer_company
    
    if request.method == 'POST' and company:
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company details updated successfully.')
            return redirect('hr_manage_company')
    else:
        form = CompanyForm(instance=company) if company else None
    
    return render(request, 'core/hr/manage_company.html', {
        'company': company,
        'form': form
    })

@login_required
@user_passes_test(is_hr)
def hr_manage_jobs(request):
    # In a real application, you would have a Job model
    # For now, let's simulate some job data
    jobs = [
        {
            'id': 1,
            'title': 'Software Developer',
            'location': 'GSEZ Zone A',
            'description': 'Looking for experienced developers',
            'requirements': 'Python, Django, JavaScript',
            'posted_date': '2023-05-15'
        },
        {
            'id': 2,
            'title': 'Network Administrator',
            'location': 'GSEZ Zone B',
            'description': 'Managing network infrastructure',
            'requirements': 'CCNA, 3+ years experience',
            'posted_date': '2023-05-20'
        }
    ]
    
    return render(request, 'core/hr/manage_jobs.html', {'jobs': jobs})

@login_required
@user_passes_test(is_hr)
def hr_job_inquiries(request):
    # In a real application, you would have a JobApplication model
    # For now, let's simulate some application data
    applications = [
        {
            'id': 1,
            'job_title': 'Software Developer',
            'applicant_name': 'John Doe',
            'applicant_email': 'john@example.com',
            'message': 'I am interested in this position',
            'status': 'pending',
            'date_applied': '2023-05-16'
        },
        {
            'id': 2,
            'job_title': 'Network Administrator',
            'applicant_name': 'Jane Smith',
            'applicant_email': 'jane@example.com',
            'message': 'I have 5 years of experience',
            'status': 'reviewed',
            'date_applied': '2023-05-21'
        }
    ]
    
    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        status = request.POST.get('status')
        
        # In a real application, you would update the status in the database
        messages.success(request, 'Application status updated successfully.')
        return redirect('hr_job_inquiries')
    
    return render(request, 'core/hr/job_inquiries.html', {'applications': applications})

# Security Dashboard
@login_required
@user_passes_test(is_security)
def security_dashboard(request):
    return render(request, 'core/security/dashboard.html')

@login_required
@user_passes_test(is_security)
def security_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        
        # Check if we have a camera capture image data
        camera_capture_data = request.POST.get('camera_capture_data')
        if camera_capture_data and camera_capture_data.startswith('data:image'):
            try:
                # Process the base64 image data
                format, imgstr = camera_capture_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Convert base64 to file
                import base64
                from django.core.files.base import ContentFile
                
                # Create a ContentFile from the decoded base64 data
                filename = f"{request.user.gsezid}.{ext}" if request.user.gsezid else f"user_{request.user.id}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=filename)
                
                # Assign the file to the user's profile_photo field
                request.user.profile_photo.save(filename, data, save=False)
            except Exception as e:
                print(f"Error processing camera capture data: {e}")
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('security_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/security/profile.html', {'form': form})

@login_required
@user_passes_test(is_security)
def security_add_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        
        # Check if we have camera capture image data
        camera_capture_data = request.POST.get('camera_capture_data')
        
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'user'
            user.save()
            
            # Process camera capture if available
            if camera_capture_data and camera_capture_data.startswith('data:image'):
                try:
                    # Process the base64 image data
                    format, imgstr = camera_capture_data.split(';base64,')
                    ext = format.split('/')[-1]
                    
                    # Convert base64 to file
                    import base64
                    from django.core.files.base import ContentFile
                    
                    # Create a ContentFile from the decoded base64 data
                    filename = f"{user.gsezid}.{ext}" if user.gsezid else f"user_{user.id}.{ext}"
                    data = ContentFile(base64.b64decode(imgstr), name=filename)
                    
                    # Assign the file to the user's profile_photo field
                    user.profile_photo.save(filename, data, save=False)
                    user.save()
                except Exception as e:
                    print(f"Error processing camera capture data: {e}")
            
            messages.success(request, 'User added successfully.')
            return redirect('security_dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/security/add_user.html', {'form': form})

@login_required
@user_passes_test(is_security)
def security_scan_qr(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            return render(request, 'core/security/user_details.html', {'user': user})
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('security_scan_qr')
    
    return render(request, 'core/security/scan_qr.html')

# API for company name suggestions
def company_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        companies = Company.objects.filter(company_name__icontains=query).values_list('company_name', flat=True)
        return JsonResponse(list(companies), safe=False)
    return JsonResponse([], safe=False)

def home_view(request):
    """
    Home page view that shows a welcome message and login form if user is not logged in,
    or a welcome back message with links to dashboard if user is logged in.
    """
    if request.user.is_authenticated:
        # User is already logged in, show welcome back message
        return render(request, 'core/index.html')
    else:
        # User is not logged in, show login form
        if request.method == 'POST':
            form = CustomAuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome, {user.first_name}!')
                    
                    # Redirect based on user type
                    if user.user_type == 'admin':
                        return redirect('admin_dashboard')
                    elif user.user_type == 'hr':
                        return redirect('hr_dashboard')
                    elif user.user_type == 'security':
                        return redirect('security_dashboard')
                    else:
                        return redirect('user_dashboard')
                else:
                    messages.error(request, 'Invalid username or password.')
        else:
            form = CustomAuthenticationForm()
        
        return render(request, 'core/login.html', {'form': form})

# Admin edit security staff
@login_required
@user_passes_test(is_admin)
def admin_edit_security(request, user_id):
    # Get the user to edit
    user_obj = get_object_or_404(User.objects.filter(user_type='security'), id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=user_obj)
        
        # Check allow_login status
        allow_login = request.POST.get('allow_login') == 'true'
        
        # Check for password change
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        if form.is_valid():
            user = form.save(commit=False)
            
            # Set is_active based on allow_login
            user.is_active = allow_login
            
            # Set new password if provided
            if password1 and password2 and password1 == password2:
                user.set_password(password1)
            elif password1 or password2:  # Only one password field is filled
                messages.warning(request, 'Both password fields must match to change password. Password not updated.')
            
            # Ensure user type remains 'security'
            user.user_type = 'security'
            
            user.save()
            
            password_msg = " Password was updated." if password1 and password2 and password1 == password2 else ""
            login_status = "with login access" if allow_login else "without login access"
            messages.success(request, f'Security staff updated successfully {login_status}.{password_msg}')
            return redirect('admin_manage_security')
    else:
        form = AdminUserEditForm(instance=user_obj)
    
    return render(request, 'core/admin/edit_security.html', {
        'user_obj': user_obj,
        'form': form,
        'is_security_staff': True
    })

# Admin edit HR staff
@login_required
@user_passes_test(is_admin)
def admin_edit_hr(request, user_id):
    # Get the user to edit
    user_obj = get_object_or_404(User.objects.filter(user_type='hr'), id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=user_obj)
        
        # Check allow_login status
        allow_login = request.POST.get('allow_login') == 'true'
        
        # Check for password change
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Get company assignment
        company_id = request.POST.get('company')
        
        if form.is_valid():
            user = form.save(commit=False)
            
            # Set is_active based on allow_login
            user.is_active = allow_login
            
            # Set new password if provided
            if password1 and password2 and password1 == password2:
                user.set_password(password1)
            elif password1 or password2:  # Only one password field is filled
                messages.warning(request, 'Both password fields must match to change password. Password not updated.')
            
            # Ensure user type remains 'hr'
            user.user_type = 'hr'
            
            # Update company association if provided
            if company_id:
                try:
                    company = Company.objects.get(id=company_id)
                    user.current_employer_company = company
                except Company.DoesNotExist:
                    messages.warning(request, f'Company with ID {company_id} not found. Company not updated.')
            
            user.save()
            
            password_msg = " Password was updated." if password1 and password2 and password1 == password2 else ""
            login_status = "with login access" if allow_login else "without login access"
            messages.success(request, f'HR staff updated successfully {login_status}.{password_msg}')
            return redirect('admin_manage_hr')
    else:
        form = AdminUserEditForm(instance=user_obj)
    
    # Get all companies for selection
    companies = Company.objects.all()
    
    return render(request, 'core/admin/edit_hr.html', {
        'user_obj': user_obj,
        'form': form,
        'companies': companies,
        'is_hr_staff': True
    })

@login_required
@user_passes_test(is_admin)
def admin_export_documents(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="documents.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Govt ID Number', 'Govt ID Photo'])  # CSV header
    
    documents = Document.objects.all().select_related('user')
    for document in documents:
        writer.writerow([
            document.user.username,
            document.govt_id_number,
            document.govt_id_photo.url if document.govt_id_photo else ''
        ])
    
    return response

@login_required
@user_passes_test(is_admin)
def admin_export_documents_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="documents_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'GovtIDNumber', 'GovtIDPhotoPath'])  # Template header
    
    # Add a sample row
    writer.writerow(['username', 'ID12345', 'path/to/photo.jpg'])
    
    return response

@login_required
@user_passes_test(is_admin)
def admin_import_documents(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('admin_import_documents')

        try:
            # Read csv file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            next(reader)  # Skip header row

            success_count = 0
            error_count = 0
            
            # Process each row
            for row in reader:
                if not row or len(row) < 3:  # Skip empty rows or rows with insufficient data
                    continue
                
                try:
                    # Extract basic required fields
                    username = row[field_indices.get('username', -1)].strip() if 'username' in field_indices else ''
                    password = row[field_indices.get('password', -1)].strip() if 'password' in field_indices else ''
                    first_name = row[field_indices.get('first_name', -1)].strip() if 'first_name' in field_indices else ''
                    last_name = row[field_indices.get('last_name', -1)].strip() if 'last_name' in field_indices else ''
                    email = row[field_indices.get('email', -1)].strip() if 'email' in field_indices else ''
                    user_type = row[field_indices.get('user_type', -1)].strip() if 'user_type' in field_indices else 'user'
                    
                    # Check if required fields are present
                    if not username or not password or not first_name or not last_name or not email:
                        error_count += 1
                        continue
                    
                    # Check if user already exists
                    if User.objects.filter(username=username).exists():
                        error_count += 1
                        continue
                    
                    # Create user with basic fields
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    # Set optional text fields
                    optional_text_fields = [
                        'middle_name', 'nationality', 'gsezid', 'current_address',
                        'permanent_address', 'current_employer', 'current_employer_emp_code',
                        'current_employer_designation', 'current_employer_department',
                        'current_employer_remarks', 'profile_full_link'
                    ]
                    
                    for field in optional_text_fields:
                        if field in field_indices and field_indices[field] < len(row):
                            value = row[field_indices[field]].strip()
                            if value:
                                setattr(user, field, value)
                    
                    # Set boolean fields
                    boolean_fields = [
                        'is_verified', 'is_required_profile_detail', 'is_printed', 'is_permanent'
                    ]
                    
                    for field in boolean_fields:
                        if field in field_indices and field_indices[field] < len(row):
                            value = row[field_indices[field]].strip().lower()
                            setattr(user, field, value in ['1', 'true', 'yes'])
                    
                    # Set date fields
                    date_fields = [
                        'date_of_birth', 'gsez_card_issue_date', 'gsez_card_expiry_date',
                        'current_employer_join_date'
                    ]
                    
                    date_field_values = {}  # Store processed date values for final debug message
                    for field in date_fields:
                        if field in field_indices and field_indices[field] < len(row):
                            value = row[field_indices[field]].strip()
                            if value:
                                try:
                                    # Try different date formats
                                    date_value = None
                                    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%d.%m.%Y']
                                    
                                    for date_format in date_formats:
                                        try:
                                            date_value = datetime.strptime(value, date_format).date()
                                            # Store the format that worked
                                            date_field_values[field] = {
                                                'raw': value,
                                                'parsed': str(date_value),
                                                'format_used': date_format
                                            }
                                            break
                                        except ValueError:
                                            continue
                                    
                                    if date_value:
                                        setattr(user, field, date_value)
                                    else:
                                        error_details.append(f"Row {row_num}: Invalid date format for {field}: {value}. Expected YYYY-MM-DD or DD/MM/YYYY")
                                except Exception as e:
                                    error_details.append(f"Row {row_num}: Error processing date {field}: {str(e)}")
                                    # Continue with other fields even if this date field fails
                    
                    # Remove the debug message - we don't want it to show in the UI
                    # (The debug info is still collected in date_field_values if needed later)
                    
                    # Set integer fields
                    if 'current_employer_rating' in field_indices and field_indices['current_employer_rating'] < len(row):
                        try:
                            rating = int(row[field_indices['current_employer_rating']].strip())
                            user.current_employer_rating = rating
                        except (ValueError, TypeError):
                            pass
                    
                    # Set company foreign key
                    if 'current_employer_company' in field_indices and field_indices['current_employer_company'] < len(row):
                        company_name = row[field_indices['current_employer_company']].strip()
                        if company_name:
                            company, created = Company.objects.get_or_create(company_name=company_name)
                            user.current_employer_company = company
                    
                    # Set JSON fields
                    json_fields = [
                        'emergency_contact_numbers', 'family_members', 
                        'previous_employers', 'qualifications'
                    ]
                    
                    for field in json_fields:
                        if field in field_indices and field_indices[field] < len(row):
                            value = row[field_indices[field]].strip()
                            if value:
                                try:
                                    # Try to parse JSON
                                    json_value = json.loads(value)
                                    setattr(user, field, value)
                                except json.JSONDecodeError:
                                    # Invalid JSON, skip this field
                                    pass
                    
                    # Set user type and status
                    if 'user_type' in field_indices and field_indices['user_type'] < len(row):
                        user_type_value = row[field_indices['user_type']].strip()
                        if user_type_value in [choice[0] for choice in User.USER_TYPE_CHOICES]:
                            user.user_type = user_type_value
                    
                    if 'status' in field_indices and field_indices['status'] < len(row):
                        status_value = row[field_indices['status']].strip()
                        if status_value in [choice[0] for choice in User.STATUS_CHOICES]:
                            user.status = status_value
                    
                    # Generate GSEZ ID if not provided
                    if not user.gsezid:
                        user.gsezid = generate_gsezid()
                    
                    # Save the user
                    user.save()
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
            
            messages.success(request, f'{success_count} users imported successfully. {error_count} users skipped (already exist or invalid data).')
        except Exception as e:
            messages.error(request, f'Error importing users: {str(e)}')
        
        return redirect('admin_manage_users')
    
    return render(request, 'core/admin/import_users.html')