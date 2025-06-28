from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import json
from datetime import datetime
import os

# Custom UserManager to override create_user method
class CustomUserManager(UserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        All fields are optional.
        """
        if not username:
            username = generate_gsezid()
        
        if not email:
            email = ""
            
        return self._create_user(username, email, password, **extra_fields)

# Function to generate GSEZ ID in the format ZIS + YY + MM + DD + 3-digit sequence number
def generate_gsezid():
    # Get current year, month and date
    now = datetime.now()
    current_year = now.year % 100  # Get last 2 digits of year
    current_month = now.month
    current_day = now.day
    
    # Create date string for filtering
    date_prefix = f'ZIS{current_year:02d}{current_month:02d}{current_day:02d}'
    
    # Find users with today's date prefix
    users_today = User.objects.filter(gsezid__startswith=date_prefix)
    
    # If no users exist with today's date prefix, start from 001
    if not users_today.exists():
        sequence_number = 1
    else:
        # Find the highest sequence number used today
        try:
            # Get all GSEZIDs for today and extract their sequence numbers
            sequence_numbers = []
            for user in users_today:
                try:
                    seq_num = int(user.gsezid[-3:])
                    sequence_numbers.append(seq_num)
                except (ValueError, IndexError):
                    continue
            
            # Find the highest sequence number
            if sequence_numbers:
                highest_sequence = max(sequence_numbers)
                # Increment by 1 if not at max
                sequence_number = min(highest_sequence + 1, 999)
            else:
                sequence_number = 1
        except Exception:
            # In case of any error, start from 001
            sequence_number = 1
    
    # Format the GSEZ ID as ZISyyMMdd###
    return f'ZIS{current_year:02d}{current_month:02d}{current_day:02d}{sequence_number:03d}'

# Function to determine upload path for profile photos using GSEZ ID
def profile_photo_path(instance, filename):
    # If the user has a GSEZ ID, use it for the filename
    if instance.gsezid:
        filename = f"{instance.gsezid}.jpg"
    # Otherwise use the username
    else:
        filename = f"{instance.username}.jpg"
    
    # Return the complete path
    return os.path.join('profile_photos', filename)

class Company(models.Model):
    company_name = models.CharField(max_length=200, unique=True)
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name_plural = "Companies"

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('security', 'Security'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
        ('terminated', 'Terminated'),
        ('under_surveillance', 'Under Surveillance'),
    )
    
    # Use custom manager
    objects = CustomUserManager()
    
    # Override username field to make it non-required
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    
    # Override email field to make it non-required
    email = models.EmailField(_('email address'), blank=True, null=True)
    
    # Override first_name field to make it non-required
    first_name = models.CharField(_('first name'), max_length=150, blank=True, null=True)
    
    # Override last_name field to make it non-required
    last_name = models.CharField(_('last name'), max_length=150, blank=True, null=True)
    
    # Personal Information
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gsez_card_issue_date = models.DateField(blank=True, null=True)
    gsez_card_expiry_date = models.DateField(blank=True, null=True)
    gsezid = models.CharField(max_length=50, unique=True, blank=True, null=True)
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    profile_full_link = models.CharField(max_length=255, blank=True, null=True)
    
    # Contact Information - Using TextField with JSON serialization instead of JSONField
    emergency_contact_numbers = models.TextField(blank=True, null=True)
    family_members = models.TextField(blank=True, null=True)  # Will store JSON string of list of dicts with name, relation, number
    
    # Address Information
    current_address = models.TextField(blank=True, null=True)
    is_permanent = models.BooleanField(default=False)
    permanent_address = models.TextField(blank=True, null=True)
    
    # Current Employment
    current_employer = models.CharField(max_length=200, blank=True, null=True)
    current_employer_join_date = models.DateField(blank=True, null=True)
    current_employer_emp_code = models.CharField(max_length=100, blank=True, null=True)
    current_employer_designation = models.CharField(max_length=100, blank=True, null=True)
    current_employer_department = models.CharField(max_length=100, blank=True, null=True)
    current_employer_company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True, related_name='employees')
    current_employer_remarks = models.TextField(blank=True, null=True)
    current_employer_rating = models.PositiveSmallIntegerField(blank=True, null=True)
    
    # Previous Employment - Using TextField with JSON serialization
    previous_employers = models.TextField(blank=True, null=True)  # Will store JSON string of list of dicts with company, join_date, leave_date, remarks, rating
    
    # Education - Using TextField with JSON serialization
    qualifications = models.TextField(blank=True, null=True)  # Will store JSON string of list of dicts with qualification, institution, year
    
    # Status and Verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_verified = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    is_required_profile_detail = models.BooleanField(default=True)
    is_printed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    # Helper methods for JSON fields
    def get_emergency_contacts(self):
        if not self.emergency_contact_numbers:
            return []
        try:
            return json.loads(self.emergency_contact_numbers)
        except:
            return []
    
    def set_emergency_contacts(self, contacts):
        self.emergency_contact_numbers = json.dumps(contacts)
    
    def get_family_members(self):
        if not self.family_members:
            return []
        try:
            return json.loads(self.family_members)
        except:
            return []
    
    def set_family_members(self, members):
        self.family_members = json.dumps(members)
    
    def get_previous_employers(self):
        if not self.previous_employers:
            return []
        try:
            return json.loads(self.previous_employers)
        except:
            return []
    
    def set_previous_employers(self, employers):
        self.previous_employers = json.dumps(employers)
    
    def get_qualifications(self):
        if not self.qualifications:
            return []
        try:
            return json.loads(self.qualifications)
        except:
            return []
    
    def set_qualifications(self, qualifications):
        self.qualifications = json.dumps(qualifications)

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    govt_id_number = models.CharField(max_length=100)
    govt_id_photo = models.ImageField(upload_to='documents/')
    
    def __str__(self):
        return f"Document for {self.user}"
