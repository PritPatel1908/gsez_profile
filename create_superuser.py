import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gsez_profile.settings')
django.setup()

from core.models import User

# Check if superuser exists
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        nationality='Default',  # Provide default values for required fields
        date_of_birth='2000-01-01',  # Default date
        gsezid='ADMIN',
        current_address='Default Address',
        user_type='admin',
        is_verified=True,
        status='active'
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists.") 