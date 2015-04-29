from experiments.models import * # Change as necessary
from django.forms import ModelForm, TextInput, CheckboxInput
from django import forms
from django.utils.translation import ugettext_lazy as _

attrs_dict = {'class': 'required'}

class ExperimentForm(ModelForm):
	class Meta:
		model = Experiment
		fields = ('title',)
		widgets = {
		'title' : TextInput(attrs={'placeholder': 'Experiment title', 'class':'experimentInput'}),
		}

class ComparisonForm(forms.Form):
	name = forms.RegexField(regex=r'^[\w.@+-]+$',
	                        max_length=200,
                        	widget=forms.TextInput(attrs={'placeholder': 'Title'}),
                            label=_("Title"),
                            error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
	attribute1 = forms.ChoiceField(widget=forms.Select(attrs=attrs_dict),
							label=_("Member"))
	attribute2 = forms.ChoiceField(widget=forms.Select(attrs=attrs_dict),
							label=_("Member"))

class ParameterForm(ModelForm):
	class Meta:
		model = Parameter
		fields = ('name','value','state',)
		widgets = {
		'name' : TextInput(attrs={'class':'parameterName'}),
		'value' : TextInput(attrs={'placeholder': 'Enter value', 'class':'parameterInput'}),
		'state' : CheckboxInput(attrs={'name': 'onoffswitch', 'class': 'onoffswitch-checkbox', 'value':True}),#BooleanField()required=False,
								#initial=False,),
								# widget=forms.RadioSelect(attrs={'name': 'onoffswitch', 'class': 'onoffswitch-checkbox'})),
		}

class DatabaseForm(forms.ModelForm):
    databases = forms.ModelMultipleChoiceField(queryset=Database.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Database
        exclude = ['name']

    def __init__(self, *args, **kwargs):
        no_standards = kwargs.pop('no_standards', False)
        super(DatabaseForm, self).__init__(*args, **kwargs)
        if no_standards:
            self.fields['databases'].choices = Database.objects.all().exclude(name='standards').values_list('id', 'name')
		# widgets = {
		# 'name' : TextInput(attrs={'placeholder': 'Experiment title', 'class':'experimentInput'}),
		# }
#class FooForm(forms.Form):
#    def __init__(self, arg1, *args, **kwargs):
#        self.arg1 = arg1
#        super(FooForm, self).__init__(*args, **kwargs)
#
#    # form fields here
#
## define the custom formset here
#from django.forms.formsets import BaseFormSet
#
#
#class FooBaseFormSet(BaseFormSet):
#    
#    def __init__(self, arg1, *args, **kwargs):
#        self.arg1 = arg1
#        super(FooBaseFormSet, self).__super__(*args, **kwargs)
#
#    
#    def _construct_forms(self):
#        self.forms = []
#        for i in xrange(self.total_form_count()):
#            self.forms.append(self._construct_form(i, arg1=self.arg1))