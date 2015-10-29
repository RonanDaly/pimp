from django import forms
from django.utils.translation import ugettext_lazy as _

class FileForm(forms.Form):
	file = forms.FileField()
	slug = forms.SlugField(max_length=50)
	project = forms.SlugField(max_length=50)
	#title = forms.RegexField(regex=r'^[\w.@+-]+$',
	#                        max_length=30,
    #                    	widget=forms.TextInput(attrs={'placeholder': 'Title'}),
    #                        label=_("Title"),
    #                        error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
	#description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description'}),
	#						label=_("Description"))