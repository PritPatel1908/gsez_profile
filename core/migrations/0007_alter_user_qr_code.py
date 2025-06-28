# Generated manually

from django.db import migrations, models
from django.db.models import F

def set_qr_code_url(apps, schema_editor):
    User = apps.get_model('core', 'User')
    for user in User.objects.all():
        if user.gsezid:
            user.qr_code = f"http://207.180.234.113/IDCARD/{user.gsezid}"
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_user_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='qr_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.RunPython(set_qr_code_url),
    ] 