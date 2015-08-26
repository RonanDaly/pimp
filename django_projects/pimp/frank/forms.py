from django import forms
from frank.models import Experiment, ExperimentalCondition, ExperimentalProtocol,\
    Sample, SampleFile, FragmentationSet, AnnotationQuery, Peak, AnnotationTool, \
    IONISATION_PROTOCOLS, FILE_TYPES
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
    detection_method = forms.ModelChoiceField(
        queryset = ExperimentalProtocol.objects.all(),
        empty_label=None,
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
            if filename.endswith('.mzXML')==False:
                self.add_error("address", "Incorrect file format. Please upload an mzXML file")
                raise forms.ValidationError("Incorrect file format. Please upload an mzXML file")
        else:
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

NIST_LIBRARIES = (
    ('mainlib', 'Main EI MS Library'),
    ('replib','Replicate EI MS Library'),
    ('nist_msms', 'Tandem (MS/MS) Library - Small Molecules'),
    ('nist_msms2', 'Tandem (MS/MS) Library - Biologically-Active Peptides'),
    ('nist_ri', 'Retention Index Library'),
)

NIST_SEARCH_PARAMS = (
    ('M', 'MS/MS in EI Library'),
    ('P','Peptide MS/MS Search in a MS/MS Library'),
    ('G', 'Generic MS/MS Search in a MS/MS Library'),
    ('I', 'Identity')
)

# Class in peak summary to select a suitable annotation tool
class AnnotationToolSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.experiment = None
        if 'experiment_object' in kwargs:
            self.experiment = kwargs.pop('experiment_object')
        super(AnnotationToolSelectionForm, self).__init__(*args, **kwargs)
        if self.experiment:
            self.fields['tool_selection']=forms.ModelChoiceField(
                queryset = AnnotationTool.objects.filter(
                    suitable_experimental_protocols = self.experiment.detection_method
                ),
                empty_label=None,
            )

    tool_selection = forms.ModelChoiceField(
        queryset=AnnotationTool.objects.all(),
        empty_label=None,
    )

# The form is used to create a Annotation Query
class AnnotationQueryForm(forms.ModelForm):
    name = forms.CharField(max_length=60, help_text="Please enter the name of the query.")

    class Meta:
        model = AnnotationQuery
        fields = (
            'name',
        )

class NISTQueryForm(AnnotationQueryForm):
    maximum_number_of_hits = forms.IntegerField(
        max_value = 20,
        min_value = 1,
        required =True,
        help_text = "Please specify the maximum number of hits returned for each spectrum"
    )
    search_type = forms.ChoiceField(
        choices = NIST_SEARCH_PARAMS,
        help_text = "Please select the required NIST search type."
    )
    query_libraries = forms.MultipleChoiceField(
        choices = NIST_LIBRARIES,
        widget=forms.CheckboxSelectMultiple(),
        help_text = "Please specify which library you wish to query."
    )

    def clean(self):
        cleaned_data = super(NISTQueryForm, self).clean()
        # get the absolute address of the uploaded file
        user_selections = cleaned_data.get('query_libraries')
        # if an absolute address has been registered
        if user_selections==None:
            self.add_error("query_libraries", "No libraries were selected. Please select at least one library to query.")
            raise forms.ValidationError("No libraries were selected. Please select at least one library to query.")


class MassBankQueryForm(AnnotationQueryForm):
    massbank_instrument_types = forms.MultipleChoiceField(
        choices= MASS_BANK_INSTRUMENT_TYPES,
        widget = forms.CheckboxSelectMultiple(),
        help_text = "Massbank supports the following instruments. Please select those that apply to the experiment.",
    )

    def clean(self):
        cleaned_data = super(MassBankQueryForm, self).clean()
        # get the absolute address of the uploaded file
        user_selections = cleaned_data.get('massbank_instrument_types')
        # if an absolute address has been registered
        if user_selections==None:
            self.add_error("massbank_instrument_types", "No instrument types were selected. Please select at least one instrument type.")
            raise forms.ValidationError("No instrument types were selected. Please select at least one instrument type.")

class NetworkSamplerQueryForm(AnnotationQueryForm):
    pass

# The form is used to specify a preferred annotation for a peak
class PreferredAnnotationForm(forms.ModelForm):
    preferred_candidate_description = forms.CharField(
        max_length=500,
        help_text="Enter justification of preferred annotation.",
        widget=forms.Textarea,
    )

    class Meta:
        model = Peak
        fields = (
            'preferred_candidate_description',
        )