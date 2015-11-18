from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


attrs_dict = {'class': 'required'}

class ProjectForm(forms.Form):
	title = forms.RegexField(regex=r'^[\w.@+-]+$',
	                        max_length=30,
                        	widget=forms.TextInput(attrs={'placeholder': 'Title'}),
                            label=_("Title"),
                            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
	description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description'}),
							label=_("Description"),
							required=False)

class EditDescriptionForm(forms.Form):
	description = forms.CharField(widget=forms.Textarea(attrs=attrs_dict),
							label=_("Description"),
							required=False)

class EditTitleForm(forms.Form):
	title = forms.RegexField(regex=r'^[\w.@+-]+$',
	                        max_length=30,
                        	widget=forms.TextInput(attrs=attrs_dict),
                            label=_('Title'),
                            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})

def is_a_valid_user(name):
	# Checks to see if name is a username or an email - for the adduser form
	try:
		any_name = User.objects.get(username=name)
	except User.DoesNotExist:
		try:
			any_email = User.objects.get(email=name)
		except User.DoesNotExist:
			raise forms.ValidationError(_('User Does Not Exist'),code='invalid_user')


class AddUserForm(forms.Form):
	name = forms.RegexField(regex=r'^[\w.@+-]+$',
	                        max_length=30,
                        	widget=forms.TextInput(attrs={'placeholder': 'Username or email address'}),
                            label=_("User name"),
                            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")},
                            validators=[is_a_valid_user])
	permission = forms.ChoiceField(widget=forms.Select(attrs=attrs_dict),
							label=_("Permission"),
							choices =(("admin","Admin"),
										("edit","Edit"),
										("read","Read")))
	



#TODO : Remove this form from project app, clone it on groups app
class GroupCreationForm(forms.Form):
	group_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Group name'}),
							label=_("Group"))
	categorie_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Categorie name'}),
							label=_("Group"))
