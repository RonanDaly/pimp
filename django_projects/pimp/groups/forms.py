from groups.models import *  # Change as necessary
from django.forms import ModelForm, TextInput
from django import forms


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['name', ]
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Experiment name', 'class': 'form-control', 'id': 'group_input'}),  # 'class': 'groupInput'
        }
        labels = {
            'name': 'Experiment name'
        }


class AttributeForm(ModelForm):
    class Meta:
        model = Attribute
        fields = ['name', ]
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Condition name', 'class': 'form-control'}),  # 'class': 'attributeInput'
        }
        labels = {
            'name': 'Condition name'
        }


class SampleAttributeForm(forms.Form):
    sample = forms.CharField(widget=forms.Textarea(attrs={'class': 'sample_attribute_input'}))
    attribute = forms.CharField(widget=forms.Textarea(attrs={'class': 'sample_attribute_input'}))


class ProjfileAttributeForm(forms.Form):
    projfile = forms.CharField(widget=forms.Textarea(attrs={'class': 'sample_attribute_input'}))
    attribute = forms.CharField(widget=forms.Textarea(attrs={'class': 'sample_attribute_input'}))
