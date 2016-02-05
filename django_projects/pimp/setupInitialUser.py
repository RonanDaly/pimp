import os
import django
import getpass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings')
django.setup()

from django.contrib.auth.models import User

if __name__ == '__main__':
    if 'PIMP_INITIAL_USERNAME' not in os.environ:
        os.environ['PIMP_INITIAL_USERNAME'] = raw_input('Username: ')
    if 'PIMP_INITIAL_EMAIL_ADDRESS' not in os.environ:
        os.environ['PIMP_INITIAL_EMAIL_ADDRESS'] = raw_input('Email: ')
    if 'PIMP_INITIAL_PASSWORD' not in os.environ:
        password = getpass.getpass('Password: ')
        passwordAgain = getpass.getpass('Password (again): ')
        while password != passwordAgain:
            print('Error: Your passwords did not match.')
            password = raw_input('Password: ')
            passwordAgain = raw_input('Password (again): ')
        os.environ['PIMP_INITIAL_PASSWORD'] = password
    if 'PIMP_INITIAL_FIRST_NAME' not in os.environ:
        os.environ['PIMP_INITIAL_FIRST_NAME'] = raw_input('First name: ')
    if 'PIMP_INITIAL_LAST_NAME' not in os.environ:
        os.environ['PIMP_INITIAL_LAST_NAME'] = raw_input('Last name: ')

    User.objects.create_superuser(
        os.environ['PIMP_INITIAL_USERNAME'],
        os.environ['PIMP_INITIAL_EMAIL_ADDRESS'],
        os.environ['PIMP_INITIAL_PASSWORD'],
        first_name=os.environ['PIMP_INITIAL_FIRST_NAME'],
        last_name=os.environ['PIMP_INITIAL_LAST_NAME']
    )
