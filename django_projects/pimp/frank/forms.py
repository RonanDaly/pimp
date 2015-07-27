from django import forms
from frank.models import Experiment, ExperimentalCondition, \
    Sample, SampleFile, FragmentationSet, AnnotationQuery, \
    IONISATION_PROTOCOLS, DETECTION_PROTOCOLS, FILE_TYPES
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# The form is used to create a new experiment
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
    ionisation_method = forms.ChoiceField(
        choices = IONISATION_PROTOCOLS,
    )
    # Creation of an experiment can include the declaration of the detection method used
    # DETECTION_PROTOCOLS is declared in the 'frank.models'
    detection_method = forms.ChoiceField(
        choices = DETECTION_PROTOCOLS
    )

    class Meta:
        model = Experiment
        fields = ('title', 'description', 'ionisation_method', 'detection_method')

# The form that is used to create a new experimental condition
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

# The form is used to add a new sample to an experiment
class SampleForm(forms.ModelForm):
    name = forms.CharField(max_length=60, help_text="Enter the name of the sample.")
    description = forms.CharField(
        widget=forms.Textarea,
        max_length=300,
        help_text="Enter a description of the sample.",
        required = False
    )
    organism = forms.CharField(max_length=60,
                               help_text="Enter the name of the organism.",
                               required = False
    )

    class Meta:
        model = Sample
        fields = (
            'name', 'description','organism'
        )
        exclude = ('experimentalCondition',)

# The form used to assign sample files to a given sample
# File types is a tuple containing the choices of file - i.e. positive and negative
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
                self.add_error("address", "Incorrect file format. Please upload an mzXML file")
                raise forms.ValidationError("Incorrect file format. Please upload an mzXML file")
        else:
            print 'No file Selected'
            self.add_error("address", "No file selected. Please upload an mzXML file")
            raise forms.ValidationError("No file selected. Please upload an mzXML file")

# The form that is used to create a new Fragmentation Set
class FragmentationSetForm(forms.ModelForm):
    name = forms.CharField(max_length=60,
                           help_text="Enter the name of the fragmentation set."
    )

    class Meta:
        model = FragmentationSet
        fields = (
            'name',
        )

# The names of the instrument types supported by the Mass Bank API for selection of the user
# Used to provide the user with checkboxes for selection of the instrument types
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

# The form is used to create a Annotation Query
class AnnotationQueryForm(forms.ModelForm):
    name = forms.CharField(max_length=60, help_text="Enter the name of the query.")
    # A series of boolean checkboxes for selection of the annotation tools used to gather annotations
    massBank = forms.BooleanField(label='massBank', required=False)
    nist = forms.BooleanField(label='NIST', required=False)
    # The parameters required for the annotation tools should be included here
    mass_bank_instrument_types = forms.MultipleChoiceField(
        choices = MASS_BANK_INSTRUMENT_TYPES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = AnnotationQuery
        fields = (
            'name', 'massBank', 'nist',
        )