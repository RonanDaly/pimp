import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings')
django.setup()

from django.contrib.auth.models import User;

User.objects.create_superuser(
	sys.argv[1],
	sys.argv[2],
	sys.argv[3],
	first_name=sys.argv[4],
	last_name=sys.argv[5]
)
