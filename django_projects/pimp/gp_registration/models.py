from django.db import models
from registration.signals import user_registered
from gp_registration.forms import MyExtendedForm

# Create your models here.
def user_created(sender, user, request, **kwargs):
    """
    Called via signals when user registers. Creates different profiles and
    associations
    """
    form = MyExtendedForm(request.POST)
    # Update first and last name for user
    user.first_name=form.data['first_name']
    user.last_name=form.data['last_name']
    user.save()

user_registered.connect(user_created)