from registration.forms import RegistrationFormUniqueEmail
from django import forms

class MyExtendedForm(RegistrationFormUniqueEmail):
	first_name = forms.CharField(widget=forms.TextInput())
	last_name = forms.CharField(widget=forms.TextInput())