import os;
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings')
django.setup()

from django.contrib.auth.models import User;

print os.getenv('PIMP_INITIAL_USERNAME')
print os.getenv('PIMP_INITIAL_EMAIL_ADDRESS')
print os.getenv('PIMP_INITIAL_PASSWORD')
print os.getenv('PIMP_INITIAL_FIRST_NAME')
print os.getenv('PIMP_INITIAL_LAST_NAME')

User.objects.create_superuser(
	os.getenv('PIMP_INITIAL_USERNAME'),
	os.getenv('PIMP_INITIAL_EMAIL_ADDRESS'),
	os.getenv('PIMP_INITIAL_PASSWORD'),
	first_name=os.getenv('PIMP_INITIAL_FIRST_NAME'),
	last_name=os.getenv('PIMP_INITIAL_LAST_NAME')
)
