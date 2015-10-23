from django import forms
from django.utils.translation import ugettext_lazy as _

attrs_dict = {'class': 'required'}

class ProjectForm(forms.Form):
	title = forms.RegexField(regex=r'^[\w.@+-]+$',
	                        max_length=30,
                        	widget=forms.TextInput(attrs={'placeholder': 'Title'}),
                            label=_("Title"),
                            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
	description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Descrition'}),
							label=_("Descrition"),
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


class AddUserForm(forms.Form):
	name = forms.RegexField(regex=r'^[\w.@+-]+$',
	                        max_length=30,
                        	widget=forms.TextInput(attrs={'placeholder': 'Username or email address'}),
                            label=_("User name"),
                            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
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
