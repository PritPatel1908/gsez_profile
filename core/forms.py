from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User, Document, Company, generate_gsezid
from django.core.exceptions import ValidationError
import json
from django.contrib.auth import authenticate

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="GSEZ ID",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your GSEZ ID'})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # First try to find a user with this GSEZID
            try:
                user_obj = User.objects.get(gsezid=username)
                # Use the actual username for authentication
                self.user_cache = authenticate(self.request, username=user_obj.username, password=password)
                
                if self.user_cache is None:
                    # Authentication failed with correct GSEZ ID but wrong password
                    raise forms.ValidationError(
                        "Invalid password for this GSEZ ID.",
                        code='invalid_login',
                    )
                else:
                    self.confirm_login_allowed(self.user_cache)
            except User.DoesNotExist:
                # Check if this is the admin account with username='admin'
                if username.upper() == 'ADMIN':
                    self.user_cache = authenticate(self.request, username='admin', password=password)
                    if self.user_cache is None:
                        raise forms.ValidationError(
                            "Invalid password for admin account.",
                            code='invalid_login',
                        )
                else:
                    # No user found with this GSEZ ID
                    raise forms.ValidationError(
                        f"No user found with GSEZ ID '{username}'.",
                        code='invalid_login',
                    )

        return self.cleaned_data

class SimpleUserRegistrationForm(UserCreationForm):
    # Remove username from the visible fields
    username = None
    
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SimpleUserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Confirm Password'
        })
        
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        # Since SimpleRegistrationForm doesn't have a gsezid field,
        # we'll generate a GSEZ ID and use it as the username
        gsez_id = generate_gsezid()
        username = gsez_id
        counter = 1
        
        # Check if username already exists, if so, append a number
        while User.objects.filter(username=username).exists():
            username = f"{gsez_id}_{counter}"
            counter += 1
            
        cleaned_data['username'] = username
        
        return cleaned_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the username from the cleaned_data
        user.username = self.cleaned_data.get('username')
        
        # Generate a GSEZ ID if not already set (should be set in clean method)
        if not user.gsezid:
            user.gsezid = generate_gsezid()
        
        # Always set the profile_full_link with the correct format
        user.profile_full_link = f"http://207.108.234.113:83/{user.gsezid}.jpg"
        
        if commit:
            user.save()
            
        return user

class UserRegistrationForm(UserCreationForm):
    # Remove username from the visible fields
    username = None
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'middle_name', 
                 'nationality', 'date_of_birth', 'gsezid', 'current_address')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gsezid': forms.TextInput(attrs={'class': 'form-control'}),
            'current_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Make all fields optional
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['nationality'].required = False
        self.fields['date_of_birth'].required = False
        self.fields['gsezid'].required = False
        self.fields['current_address'].required = False
        self.fields['email'].required = False
        
        # Make GSEZ ID field readonly
        self.fields['gsezid'].widget.attrs.update({'readonly': 'readonly'})
        
    def clean(self):
        cleaned_data = super().clean()
        gsezid = cleaned_data.get('gsezid')
        
        # Use GSEZ ID as username
        if gsezid:
            username = gsezid
            counter = 1
            
            # Check if username already exists, if so, append a number
            while User.objects.filter(username=username).exists():
                username = f"{gsezid}_{counter}"
                counter += 1
                
            cleaned_data['username'] = username
        
        # No field validation - all fields are optional
                
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the username from the cleaned_data
        user.username = self.cleaned_data.get('username')
        
        # Generate a unique GSEZ ID if not provided
        if not user.gsezid:
            user.gsezid = generate_gsezid()
        
        # Always set the profile_full_link with the correct format
        user.profile_full_link = f"http://207.108.234.113:83/{user.gsezid}.jpg"
        
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    # Emergency contact fields
    emergency_contact_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    emergency_contact_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Family member fields
    family_member_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    family_member_relation = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    family_member_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Previous employer fields
    previous_employer_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    previous_employer_join_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    previous_employer_leave_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    previous_employer_remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    previous_employer_rating = forms.IntegerField(required=False, min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    # Qualification fields
    qualification = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    institution = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    year_of_passing = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Exclude GSEZ ID from form fields to prevent updating
        if 'gsezid' in self.fields:
            self.fields['gsezid'].widget.attrs.update({'readonly': 'readonly', 'disabled': 'disabled'})
        
        # Make username field readonly but not disabled so it can be submitted
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({'readonly': 'readonly'})

    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'username', 'nationality', 
                 'date_of_birth', 'gsez_card_issue_date', 'gsez_card_expiry_date', 
                 'profile_photo', 'current_address', 'is_permanent', 'permanent_address',
                 'current_employer', 'current_employer_join_date', 'current_employer_emp_code',
                 'current_employer_designation', 'current_employer_department', 'current_employer_company',
                 'current_employer_remarks', 'current_employer_rating')
        # Explicitly exclude gsezid field and profile_full_link
        exclude = ('gsezid', 'profile_full_link')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gsez_card_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gsez_card_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'current_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_employer': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_employer_emp_code': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_department': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_company': forms.Select(attrs={'class': 'form-control'}),
            'current_employer_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'current_employer_rating': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        instance = super(UserProfileForm, self).save(commit=False)
        
        # Get original GSEZID from the instance before form changes
        if self.instance and self.instance.pk:
            original_instance = User.objects.get(pk=self.instance.pk)
            # Always preserve the original GSEZ ID
            instance.gsezid = original_instance.gsezid
            
            gsezid = instance.gsezid
            
            # Use only GSEZID for username
            if gsezid:
                username = gsezid
                
                # Check if generated username already exists for another user
                counter = 1
                base_username = username
                while User.objects.filter(username=username).exclude(pk=instance.pk).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                instance.username = username
                
                # Always set the profile_full_link with the correct format
                instance.profile_full_link = f"http://207.108.234.113:83/{gsezid}.jpg"
        
        # Handle emergency contacts
        if self.cleaned_data.get('emergency_contact_name') and self.cleaned_data.get('emergency_contact_number'):
            emergency_contacts = instance.get_emergency_contacts()
            emergency_contacts.append({
                'name': self.cleaned_data['emergency_contact_name'],
                'number': self.cleaned_data['emergency_contact_number']
            })
            instance.set_emergency_contacts(emergency_contacts)
        
        # Handle family members
        if self.cleaned_data.get('family_member_name') and self.cleaned_data.get('family_member_relation'):
            family_members = instance.get_family_members()
            family_members.append({
                'name': self.cleaned_data['family_member_name'],
                'relation': self.cleaned_data['family_member_relation'],
                'number': self.cleaned_data.get('family_member_number', '')
            })
            instance.set_family_members(family_members)
        
        # Handle previous employers
        if self.cleaned_data.get('previous_employer_name'):
            join_date = self.cleaned_data.get('previous_employer_join_date')
            leave_date = self.cleaned_data.get('previous_employer_leave_date')
            
            # Convert dates to strings for JSON serialization
            if join_date:
                join_date = join_date.strftime('%Y-%m-%d') if hasattr(join_date, 'strftime') else join_date
            if leave_date:
                leave_date = leave_date.strftime('%Y-%m-%d') if hasattr(leave_date, 'strftime') else leave_date
            
            previous_employers = instance.get_previous_employers()
            previous_employers.append({
                'company': self.cleaned_data['previous_employer_name'],
                'join_date': join_date,
                'leave_date': leave_date,
                'remarks': self.cleaned_data.get('previous_employer_remarks', ''),
                'rating': self.cleaned_data.get('previous_employer_rating', '')
            })
            instance.set_previous_employers(previous_employers)
        
        # Handle qualifications
        if self.cleaned_data.get('qualification') and self.cleaned_data.get('institution'):
            qualifications = instance.get_qualifications()
            qualifications.append({
                'qualification': self.cleaned_data['qualification'],
                'institution': self.cleaned_data['institution'],
                'year': self.cleaned_data.get('year_of_passing', '')
            })
            instance.set_qualifications(qualifications)
        
        if commit:
            instance.save()
        return instance

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('govt_id_number', 'govt_id_photo')
        widgets = {
            'govt_id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'govt_id_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('company_name',)
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserManagementForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('status', 'is_verified', 'user_type', 'is_printed')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }

class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            # Basic Information
            'username', 'email', 'first_name', 'middle_name', 'last_name',
            # Personal Information
            'nationality', 'date_of_birth', 'gsezid', 
            'gsez_card_issue_date', 'gsez_card_expiry_date', 'profile_photo', 'profile_full_link',
            # Address Information
            'current_address', 'is_permanent', 'permanent_address',
            # Current Employment
            'current_employer', 'current_employer_join_date', 'current_employer_emp_code',
            'current_employer_designation', 'current_employer_department', 
            'current_employer_company', 'current_employer_remarks', 'current_employer_rating',
            # Status and Verification
            'status', 'is_verified', 'user_type', 'is_printed'
        ]
        widgets = {
            # Basic Information
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            # Personal Information
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gsezid': forms.TextInput(attrs={'class': 'form-control'}),
            'gsez_card_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gsez_card_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'profile_full_link': forms.TextInput(attrs={'class': 'form-control'}),
            # Address Information
            'current_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # Current Employment
            'current_employer': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_employer_emp_code': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_department': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_company': forms.Select(attrs={'class': 'form-control'}),
            'current_employer_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'current_employer_rating': forms.NumberInput(attrs={'class': 'form-control'}),
            # Status and Verification
            'status': forms.Select(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }

    # Emergency contact fields
    emergency_contact_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    emergency_contact_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Family member fields
    family_member_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    family_member_relation = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    family_member_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Previous employer fields
    previous_employer_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    previous_employer_join_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    previous_employer_leave_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    previous_employer_remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    previous_employer_rating = forms.IntegerField(required=False, min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    # Qualification fields
    qualification = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    institution = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    year_of_passing = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super(AdminUserEditForm, self).__init__(*args, **kwargs)
        
        # Always make GSEZ ID field readonly in edit mode
        self.fields['gsezid'].widget.attrs.update({'readonly': 'readonly', 'disabled': 'disabled'})
        
        # Make username field readonly but not disabled so it can be submitted with form
        self.fields['username'].widget.attrs.update({'readonly': 'readonly'})
    
    def save(self, commit=True):
        instance = super(AdminUserEditForm, self).save(commit=False)
        
        # Get original GSEZID from the instance before form changes
        if self.instance and self.instance.pk:
            original_instance = User.objects.get(pk=self.instance.pk)
            # Always preserve the original GSEZ ID
            instance.gsezid = original_instance.gsezid

            gsezid = instance.gsezid
            
            # Use only GSEZID for username
            if gsezid:
                username = gsezid
                
                # Check if generated username already exists for another user
                counter = 1
                base_username = username
                while User.objects.filter(username=username).exclude(pk=instance.pk).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                instance.username = username
                
                # Always set the profile_full_link with the correct format
                instance.profile_full_link = f"http://207.108.234.113:83/{gsezid}.jpg"
        
        # Handle emergency contacts
        if self.cleaned_data.get('emergency_contact_name') and self.cleaned_data.get('emergency_contact_number'):
            emergency_contacts = instance.get_emergency_contacts()
            emergency_contacts.append({
                'name': self.cleaned_data['emergency_contact_name'],
                'number': self.cleaned_data['emergency_contact_number']
            })
            instance.set_emergency_contacts(emergency_contacts)
        
        # Handle family members
        if self.cleaned_data.get('family_member_name') and self.cleaned_data.get('family_member_relation'):
            family_members = instance.get_family_members()
            family_members.append({
                'name': self.cleaned_data['family_member_name'],
                'relation': self.cleaned_data['family_member_relation'],
                'number': self.cleaned_data.get('family_member_number', '')
            })
            instance.set_family_members(family_members)
        
        # Handle previous employers
        if self.cleaned_data.get('previous_employer_name'):
            join_date = self.cleaned_data.get('previous_employer_join_date')
            leave_date = self.cleaned_data.get('previous_employer_leave_date')
            
            # Convert dates to strings for JSON serialization
            if join_date:
                join_date = join_date.strftime('%Y-%m-%d') if hasattr(join_date, 'strftime') else join_date
            if leave_date:
                leave_date = leave_date.strftime('%Y-%m-%d') if hasattr(leave_date, 'strftime') else leave_date
            
            previous_employers = instance.get_previous_employers()
            previous_employers.append({
                'company': self.cleaned_data['previous_employer_name'],
                'join_date': join_date,
                'leave_date': leave_date,
                'remarks': self.cleaned_data.get('previous_employer_remarks', ''),
                'rating': self.cleaned_data.get('previous_employer_rating', '')
            })
            instance.set_previous_employers(previous_employers)
        
        # Handle qualifications
        if self.cleaned_data.get('qualification') and self.cleaned_data.get('institution'):
            qualifications = instance.get_qualifications()
            qualifications.append({
                'qualification': self.cleaned_data['qualification'],
                'institution': self.cleaned_data['institution'],
                'year': self.cleaned_data.get('year_of_passing', '')
            })
            instance.set_qualifications(qualifications)
        
        if commit:
            instance.save()
        return instance

class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            # Basic Information
            'username', 'email', 'first_name', 'middle_name', 'last_name',
            # Personal Information
            'nationality', 'date_of_birth', 'gsezid', 
            'gsez_card_issue_date', 'gsez_card_expiry_date', 'profile_photo', 'profile_full_link',
            # Address Information
            'current_address', 'is_permanent', 'permanent_address',
            # Current Employment
            'current_employer', 'current_employer_join_date', 'current_employer_emp_code',
            'current_employer_designation', 'current_employer_department', 
            'current_employer_company', 'current_employer_remarks', 'current_employer_rating',
            # Status and Verification
            'status', 'is_verified', 'user_type', 'is_printed', 'password1', 'password2'
        ]
        widgets = {
            # Basic Information
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            # Personal Information
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gsezid': forms.TextInput(attrs={'class': 'form-control'}),
            'gsez_card_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gsez_card_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'profile_full_link': forms.TextInput(attrs={'class': 'form-control'}),
            # Address Information
            'current_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # Current Employment
            'current_employer': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_employer_emp_code': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_department': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer_company': forms.Select(attrs={'class': 'form-control'}),
            'current_employer_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'current_employer_rating': forms.NumberInput(attrs={'class': 'form-control'}),
            # Status and Verification
            'status': forms.Select(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    # Emergency contact fields
    emergency_contact_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    emergency_contact_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Family member fields
    family_member_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    family_member_relation = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    family_member_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Previous employer fields
    previous_employer_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    previous_employer_join_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    previous_employer_leave_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    previous_employer_remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    previous_employer_rating = forms.IntegerField(required=False, min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    # Qualification fields
    qualification = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    institution = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    year_of_passing = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super(AdminUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Make all fields optional for admin creation
        for field in self.fields:
            if field not in ['username', 'password1', 'password2']:
                self.fields[field].required = False
                
        # Check if this is a first employee (will be set from view context)
        # This won't modify the widget here, but will be used in the template
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if not user.gsezid:
            user.gsezid = generate_gsezid()
            
        # Set username to GSEZ ID
        user.username = user.gsezid
        
        # Always set the profile_full_link with the correct format
        user.profile_full_link = f"http://207.108.234.113:83/{user.gsezid}.jpg"
            
        # Convert date fields to proper format for existing/basic record
        if user.date_of_birth and hasattr(user.date_of_birth, 'strftime'):
            user.date_of_birth = user.date_of_birth
        
        if user.gsez_card_issue_date and hasattr(user.gsez_card_issue_date, 'strftime'):
            user.gsez_card_issue_date = user.gsez_card_issue_date
            
        if user.gsez_card_expiry_date and hasattr(user.gsez_card_expiry_date, 'strftime'):
            user.gsez_card_expiry_date = user.gsez_card_expiry_date
            
        if user.current_employer_join_date and hasattr(user.current_employer_join_date, 'strftime'):
            user.current_employer_join_date = user.current_employer_join_date
        
        if commit:
            user.save()

        # Process emergency contacts
        if self.cleaned_data.get('emergency_contact_name') and self.cleaned_data.get('emergency_contact_number'):
            emergency_contacts = []
            emergency_contacts.append({
                'name': self.cleaned_data['emergency_contact_name'],
                'number': self.cleaned_data['emergency_contact_number']
            })
            user.set_emergency_contacts(emergency_contacts)
            
        # Process family members
        if self.cleaned_data.get('family_member_name') and self.cleaned_data.get('family_member_relation'):
            family_members = []
            family_members.append({
                'name': self.cleaned_data['family_member_name'],
                'relation': self.cleaned_data['family_member_relation'],
                'number': self.cleaned_data.get('family_member_number', '')
            })
            user.set_family_members(family_members)
            
        # Process previous employer
        if self.cleaned_data.get('previous_employer_name'):
            join_date = self.cleaned_data.get('previous_employer_join_date')
            leave_date = self.cleaned_data.get('previous_employer_leave_date')
            
            # Convert dates to strings for JSON serialization
            if join_date:
                join_date = join_date.strftime('%Y-%m-%d') if hasattr(join_date, 'strftime') else join_date
            if leave_date:
                leave_date = leave_date.strftime('%Y-%m-%d') if hasattr(leave_date, 'strftime') else leave_date
                
            previous_employers = []
            previous_employers.append({
                'company': self.cleaned_data['previous_employer_name'],
                'join_date': join_date,
                'leave_date': leave_date,
                'remarks': self.cleaned_data.get('previous_employer_remarks', ''),
                'rating': self.cleaned_data.get('previous_employer_rating', 0)
            })
            user.set_previous_employers(previous_employers)
            
        # Process qualification
        if self.cleaned_data.get('qualification') and self.cleaned_data.get('institution'):
            qualifications = []
            qualifications.append({
                'qualification': self.cleaned_data['qualification'],
                'institution': self.cleaned_data['institution'],
                'year': self.cleaned_data.get('year_of_passing', '')
            })
            user.set_qualifications(qualifications)
            
        if commit:
            user.save()

        return user