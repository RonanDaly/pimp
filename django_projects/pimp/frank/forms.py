from django import forms
from frank.models import Experiment, ExperimentalCondition, \
    Sample, SampleFile, FragmentationSet, AnnotationQuery, IONISATION_PROTOCOLS, DETECTION_PROTOCOLS, FILE_TYPES
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# The form is used to create a new user
#### NOT NEEDED ANYMORE, USE PiMP SignUp #####
class SignUpForm(forms.ModelForm):
    username = forms.CharField(max_length=60, help_text="Enter your username.")
    email = forms.CharField(max_length=60, help_text="Enter your email.", required = False)
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Enter your password.")

    class Meta:
        # Update the User model of the database
        model = User
        fields = ('username', 'email', 'password')

# The form that is used to new experiment
class ExperimentForm(forms.ModelForm):
    title = forms.CharField(max_length=60, help_text="Enter the name of the experiment.")
    description = forms.CharField(
        widget=forms.Textarea,
        max_length=300,
        help_text="Enter a description of the experiment.",
        required = False
    )
    # Creation of an experiment can include the declaration of the ionisation protocol used
    # IONISATION_PROTOCOLS is declared in 'frank.models'
    ionisationMethod = forms.ChoiceField(
        choices = IONISATION_PROTOCOLS,
        required = False
    )
    # Creation of an experiment can include the declaration of the detection method used
    # DETECTION_PROTOCOLS is declared in the 'frank.models'
    detectionMethod = forms.ChoiceField(
        choices = DETECTION_PROTOCOLS
    )

    class Meta:
        model = Experiment
        fields = ('title', 'description', 'ionisationMethod', 'detectionMethod')

# The form that is used to new experimental condition
class ExperimentalConditionForm(forms.ModelForm):
    name = forms.CharField(max_length=60, help_text="Enter the name of the experiment condition.")
    description = forms.CharField(
        widget=forms.Textarea,
        max_length=300,
        help_text="Enter a description of the condition.",
        required = False
    )

    class Meta:
        model = ExperimentalCondition
        fields = (
            'name', 'description',
        )

# The form is used to create a add a new sample to an experiment
class SampleForm(forms.ModelForm):
    name = forms.CharField(max_length=60, help_text="Enter the name of the sample.")
    description = forms.CharField(
        widget=forms.Textarea,
        max_length=300,
        help_text="Enter a description of the sample.",
        required = False
    )
    organism = forms.CharField(max_length=60, help_text="Enter the name of the organism.", required = False)

    class Meta:
        model = Sample
        fields = (
            'name', 'description','organism'
        )
        exclude = ('experimentalCondition',)

# The form used to assign sample files to a given sample
# File types is a tuple containing the choices of file - i.e. positive and negative, but this could be expanded to
# include pooled samples
class SampleFileForm(forms.ModelForm):
    polarity = forms.ChoiceField(
        choices = FILE_TYPES
    )
    address = forms.FileField()

    class Meta:
        model = SampleFile
        fields = (
            'polarity', 'address',
        )
        exclude = (
            'sample',
        )

    # the 'clean' method here is used to validate that the extension of the file
    # uploaded by the user is of type mzXML
    def clean(self):
        cleaned_data = super(SampleFileForm, self).clean()
        # get the absolute address of the uploaded file
        inputFile = cleaned_data.get('address')
        # if an absolute address has been registered
        if inputFile:
            #derive the name of the file
            filename = inputFile.name
            # check the file extension is '.mzXML'
            if filename.endswith('.mzXML'):
                print 'Valid file'
            else:
                print 'Invalid file format'
                raise forms.ValidationError("Incorrect file format. Please upload mzXML files")

## TO DO: create an analysis form class
# The form that is used to new experimental condition
class FragmentationSetForm(forms.ModelForm):
    name = forms.CharField(max_length=60, help_text="Enter the name of the fragmentation set.")

    class Meta:
        model = FragmentationSet
        fields = (
            'name',
        )


MASS_BANK_INSTRUMENT_TYPES = (
    ('EI-B', 'EI-B'),
    ('EI-EBEB', 'EI-EBEB'),
    ('GC-EI-QQ', 'GC-EI-QQ'),
    ('GC-EI-TOF', 'GC-EI-TOF'),
    ('CE-ESI-TOF', 'CE-ESI-TOF'),
    ('ESI-ITFT', 'ESI-ITFT'),
    ('ESI-ITTOF', 'ESI-ITTOF'),
    ('LC-ESI-IT', 'LC-ESI-IT'),
    ('LC-ESI-ITFT', 'LC-ESI-ITFT'),
    ('LC-ESI-ITTOF', 'LC-ESI-ITTOF'),
    ('LC-ESI-Q', 'LC-ESI-Q'),
    ('LC-ESI-QFT', 'LC-ESI-QFT'),
    ('LC-ESI-QIT', 'LC-ESI-QIT'),
    ('LC-ESI-QQ', 'LC-ESI-QQ'),
    ('LC-ESI-QTOF', 'LC-ESI-QTOF'),
    ('LC-ESI-TOF', 'LC-ESI-TOF'),
)

class AnnotationQueryForm(forms.ModelForm):
    name = forms.CharField(max_length=60, help_text="Enter the name of the query.")
    massBank = forms.BooleanField(label='massBank')
    mass_bank_instrument_types = forms.MultipleChoiceField(choices = MASS_BANK_INSTRUMENT_TYPES, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = AnnotationQuery
        fields = (
            'name', 'massBank',
        )