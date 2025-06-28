from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_user_profile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_full_link',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]