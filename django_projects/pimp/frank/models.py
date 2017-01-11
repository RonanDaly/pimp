__author__ = 'Scott Greig'

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import os
from django.conf import settings
from django.db.models import Max
from django.core.exceptions import ValidationError

from data.models import Peak as PimpPeak
from experiments.models import Analysis as PimpAnalysis
from projects.models import Project as PimpProject

"""
 The default Django User model provides the following attributes:
 username
 password
 email
 first_name
 last_name
"""

# A tuple containing the file 'types' ie. the polarity of the file
FILE_TYPES = (
    ('Positive', 'Positive'),
    ('Negative', 'Negative'),
)

# A tuple containing the 'state' of an analysis to provide the user with feedback
ANALYSIS_STATUS = (
    ('Submitted', 'Submitted'),
    ('Processing', 'Processing'),
    ('Completed Successfully', 'Completed Successfully'),
    ('Completed with Errors', 'Completed with Errors'),
)

# Define the choices for ionisation protocol
IONISATION_PROTOCOLS = (
    ('ESI', 'Electrospray Ionisation'),
    ('EII', 'Electron Impact Ionisation'),
    # Additional ionisation protocols could be added here if necessary
)


def _get_upload_file_name(instance, filename):
    """
    Method to determine, and create the filepath of the upload location for an mzXML file
    :param instance:    SampleFile instance for upload
    :param filename:    The name of the file including the extension (e.g. "myfile.mzXML")
    :return: upload_location    String containing the filepath of the uploaded file
    """

    # Retrive the sample, experimental condition and experiment to which the sample file is to be associated
    sample_object = instance.sample
    experimental_condition_object = sample_object.experimental_condition
    experiment_object = experimental_condition_object.experiment
    # The directory of the file upload is concatinated to the root directory
    filepath = os.path.join(settings.MEDIA_ROOT,
                            'frank',
                            experiment_object.created_by.username,
                            experiment_object.slug,
                            experimental_condition_object.slug,
                            sample_object.slug,
                            instance.polarity
                            )
    try:
        # If the directory doesn't exist then it must be created.
        os.makedirs(filepath)
    except OSError as e:
        if e.errno == 17:
            # Directory already exists so no need for it to be created
            pass
    # Finally, the filename is contatinated to the directory
    upload_location = os.path.join(filepath, filename)
    existing_file = os.path.isfile(upload_location)
    if existing_file:
        raise ValidationError('Files cannot be duplicated')
    return upload_location



def alternativeSave(MyModel, self, *args, **kwargs):

    """
    A save method to use when we use the id as the slug
    We need to save twice but don't want to write to the DB twice
    - therefore force-insert is removed from **kwargs for the second save (kwargsUpdate)
    """
    super(MyModel, self).save(*args, **kwargs)
    self.slug = self.id
    kwargsUpdate = dict(kwargs)
    kwargsUpdate['force_update'] = True
    if 'force_insert' in kwargsUpdate:
        del kwargsUpdate['force_insert']
    super(MyModel, self).save(*args, **kwargsUpdate)


class Experiment(models.Model):
    """
    Model class containing the details of the experiment. Analogous to a PiMP project.
    """

    title = models.CharField(max_length=250, blank=False)
    description = models.CharField(max_length=250)
    created_by = models.ForeignKey(User, related_name="experiment_creator")
    time_created = models.DateTimeField(auto_now=True)
    ionisation_method = models.CharField(max_length=250, choices=IONISATION_PROTOCOLS)
    detection_method = models.ForeignKey('ExperimentalProtocol')
    users = models.ManyToManyField(User, through='UserExperiment', through_fields=('experiment', 'user'))
    slug = models.SlugField(default='')

    """
    For integration, this model could be integrated with the PiMP Project model
    if the ionisation_method and detection_method fields were added in PiMP. These
    are used to distinguish between the distinct experimental types implemented in
    Frank and are therefore required. Alternatively, a ForeignKey reference to a PiMP
    project could be added, to ensure Frank remains stand-alone.
    """

    def save(self, *args, **kwargs):
        """
        Override the existing save method to update the slugfield to reflect the id this requires an alternative save
        :param args:    Any arguments passed to the save method
        :param kwargs:  Any keyword arguments passed to the save method
        """
        alternativeSave(Experiment, self, *args, **kwargs)



    def __unicode__(self):
        """
        Method to return a unicode representation of the model instance
        :return: String:    A string containing the instance id and experiment title
        """

        return 'Experiment '+str(self.id)+': '+str(self.title)


class UserExperiment(models.Model):
    """
    Model class defining the users with access to each Experiment Model instance
    """

    user = models.ForeignKey(User)
    experiment = models.ForeignKey(Experiment)

    def __unicode__(self):
        """
        Method to return a unicode representation of the model instance
        :return: String:    A string containing the username and experiment title
        """

        return self.user.username + ' access to ' + self.experiment.title


class ExperimentalCondition(models.Model):
    """
    Model class defining an experimental condition in the experiment.
    """
    name = models.CharField(max_length=250, blank=False)
    description = models.CharField(max_length=250)
    experiment = models.ForeignKey(Experiment)
    slug = models.SlugField(default='')


    def save(self, *args, **kwargs):
        """
        Method overriding the 'Model' superclass save method
        :param args:    Arguments passed to the save method
        :param kwargs:  Keyword arguments passed to the save method
         """
        alternativeSave(ExperimentalCondition, self, *args, **kwargs)


    def __unicode__(self):
        """
        Method to return a unicode representation of the model instance
        :return: String:    A string containing the experimental condition and the title of the experiment
        """

        return self.name+' in '+self.experiment.title


class Sample(models.Model):
    """
    Model class defining an instance of an experimental sample
    """

    name = models.CharField(max_length=250, blank=False)
    description = models.CharField(max_length=250, blank=False)
    experimental_condition = models.ForeignKey(ExperimentalCondition)
    organism = models.CharField(max_length=250)
    slug = models.SlugField(default='')

    def save(self, *args, **kwargs):
        """
        Method to override the save method of the superclass 'Model'
        :param args:    Arguments passed to the save method
        :param kwargs:  Keyword arguments passed to the save method
        """

        # The slug field is populated with the primary key, id.

        alternativeSave(Sample, self, *args, **kwargs)



    def __unicode__(self):
        """
        Method to return a unicode representation of the Sample.
        :return: String:    A string representation including the id and title of the associated experiment
        """

        return 'Sample '+str(self.id) + ' in ' + self.experimental_condition.experiment.title


class SampleFile(models.Model):
    """
    Model class defining the mzXML files associated with an experimental sample
    """

    name = models.CharField(max_length=250, blank=False)
    polarity = models.CharField(max_length=250)
    sample = models.ForeignKey(Sample, blank=False)
    address = models.FileField(upload_to=_get_upload_file_name, max_length=500)


    @models.permalink
    def get_absolute_url(self):
        return ('upload-new-fragFile',)

    def __unicode__(self):
        """
        Method to return a unicode representation of the SampleFile instance
        :return: String:    A string representation of the sample file name
        """

        return self.name


class FragmentationSet(models.Model):
    """
    Model instance to define the collection of peaks derived from the sample files of an experiment
    """

    name = models.CharField(max_length=250)
    experiment = models.ForeignKey(Experiment)
    time_created = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=250, choices=ANALYSIS_STATUS, default='Submitted')
    slug = models.SlugField(default='')

    def save(self, *args, **kwargs):
        """
        Method to override the save method of the Model superclass
        :param args:    The arguments passed to the save method
        :param kwargs:  The keyword argument passed to the save method
        """

        # The slug is the id of the FragmentationSet instance

        alternativeSave(FragmentationSet, self, *args, **kwargs)

    def __unicode__(self):
        """
        Method to return a unicode representation of the FragmentationSet
        :return: String:    The string contains the 'id' of the FragmentationSet
        """

        return self.name + ' (from experiment ' + self.experiment.title + ')'


class AnnotationQuery(models.Model):
    """
    Model class defining a query made to one of the Annotation Tools - termed 'Annotation Query'
    """

    name = models.CharField(max_length=250)
    fragmentation_set = models.ForeignKey(FragmentationSet)
    time_created = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=250, choices=ANALYSIS_STATUS, default='Defined')
    slug = models.SlugField(unique=True)
    annotation_tool = models.ForeignKey('AnnotationTool')
    # The annotation_tool_params are a jsonpickle dict of any additional search parameters required
    # by the AnnotationTool itself
    annotation_tool_params = models.CharField(max_length=1000, null=True)
    # Some AnnotationTools may subquery an existing set of CandidateAnnotations
    source_annotation_queries = models.ManyToManyField('self', through='AnnotationQueryHierarchy', symmetrical=False)

    def save(self, *args, **kwargs):
        """
        Method to override the save method of the Model superclass
        :param args:    Arguments passed to the save method
        :param kwargs:  Keyword arguments passed to the save method
        """

        # The slug is the id of the AnnotationQuery instance
        alternativeSave(AnnotationQuery, self, *args, **kwargs)

    def __unicode__(self):
        """
        Method to return a unicode representation of the AnnotationQuery
        :return: String:    A string containing the 'id' of the AnnotationQuery
        """

        return 'Annotation Query '+str(self.id)


class AnnotationTool (models.Model):
    """
    Model class representing an AnnotationTool - i.e. any tool which creates or modifies CandidateAnnotations
    """

    name = models.CharField(max_length=250, blank=False, unique=True)
    suitable_experimental_protocols = models.ManyToManyField('ExperimentalProtocol', through='AnnotationToolProtocol')
    default_params = models.CharField(max_length=500)
    # The tool's default parameters are a jsonpickle dict of any default params required by the tool
    # such as filepaths etc.
    slug = models.SlugField(default='')

    def save(self, *args, **kwargs):
        """
        Method to override the Model superclass save method
        :param args:    Arguments passed to the method
        :param kwargs:  Keyword arguments passed to the method
        """

        # The slug for the AnnotationTool is simply its name
        self.slug = slugify(self.name)
        super(AnnotationTool, self).save(*args, **kwargs)

    def __unicode__(self):
        """
        Method to return a unicode representation of the AnnotationTool instance
        :return: String A string representation of the tool's name
        """

        return self.name


class Compound(models.Model):
    """
    Model class representing a Compound identified by spectral database searches
    """

    name = models.CharField(max_length=250)
    formula = models.CharField(max_length=250)
    exact_mass = models.DecimalField(decimal_places=10, max_digits=20, null=True)
    # Inchikey included to improve compatability with PiMP, however, it should be noted that
    # at present this unique identifier is not returned by any of the existing implemented tools
    inchikey = models.CharField(max_length=500, null=True)
    #csid from the ChemSpider DB
    csid = models.CharField(max_length=500, null=True)
    # cas_code is returned from NIST spectral search and therefore has been stored
    cas_code = models.CharField(max_length=500, null=True)
    # Human Metabolome Database (HMDB) ID
    hmdb_id = models.CharField(max_length=500, null=True)
    annotation_tool = models.ManyToManyField(AnnotationTool, through='CompoundAnnotationTool')
    slug = models.SlugField(unique=True)

    def get_image_url(self):

        if self.csid:
            return 'http://www.chemspider.com/ImagesHandler.ashx?id=' + self.csid
        else:
            return None

    image_url = property(get_image_url)

    def get_cs_url(self):

        if self.csid:
            return 'http://www.chemspider.com/Chemical-Structure.' + self.csid + '.html'
        else:
            return None

    cs_url = property(get_cs_url)

    def get_hmdb_url(self):

        if self.hmdb_id:
            return 'http://www.hmdb.ca/metabolites/' + self.hmdb_id
        else:
            return None

    hmdb_url = property(get_cs_url)

    def save(self, *args, **kwargs):
        """
        Method to override the save method of the Model superclass
        :param args:    Arguments passed to the method
        :param kwargs:  Keyword arguments passed to the method
        """

        """
        At the time of implementation it made sense to ensure the compound slug remains static as this
        is not user defined. However, the name of the compound could not be used as, in some instances,
        the chemical name exceeds the maximum number of chars of the slugfield. The formula would not be
        suitable because of isomers.
        """
        if not self.id:
            # i.e. if the instance does not have a primary key it hasn't yet been commited to the database
            compound_id_max = Compound.objects.aggregate(Max('id'))['id__max']
            # Try to determine the maximum primary key of the existing compounds in the database
            if compound_id_max is None:
                # if none is returned, this would be the first compound
                compound_id_max = 0
            # Increment the id by one
            compound_number = compound_id_max+1
            self.slug = slugify('Compound: ' + str(compound_number) + 'Formula: ' + str(self.formula))
        super(Compound, self).save(*args, **kwargs)

    def __unicode__(self):
        """
        Method to return a unicode representation of the compound
        :return: String:    This is simply the name of the compound
        """

        return self.name


class Peak(models.Model):
    """
    Model class defining a peak, characterised by a mass, retention time and intensity
    """

    # Store where the peak originated from
    source_file = models.ForeignKey(SampleFile, blank=False)
    mass = models.DecimalField(decimal_places=10, max_digits=20)
    retention_time = models.DecimalField(decimal_places=10, max_digits=20)
    intensity = models.DecimalField(decimal_places=10, max_digits=30)
    # Each peak can only ever have one parent ion, which should also be present in the peak table
    parent_peak = models.ForeignKey('self', null=True)
    msn_level = models.IntegerField()
    # Each peak can have any number of candidate annotations
    annotations = models.ManyToManyField(Compound, through='CandidateAnnotation')
    # Although the source file is stored, the fragmentation set the peak is derived from is included
    fragmentation_set = models.ForeignKey(FragmentationSet)
    slug = models.SlugField(unique=True)
    # A preferred annotation can be allocated to the Peak, alongside a description and the identity of the user
    # who specfied the preference.
    preferred_candidate_annotation = models.ForeignKey(
        'CandidateAnnotation', null=True, related_name="preferred_annotation",
        on_delete = models.SET_NULL)
    preferred_candidate_description = models.CharField(max_length=500, null=True)
    preferred_candidate_user_selector = models.ForeignKey(User, null=True)
    preferred_candidate_updated_date = models.DateTimeField(null=True)

    """
    During implementation it was considered as to whether or not the preferred annotation
    should be seperate model in itself and is a transitive dependency. Although it could be
    a distinct table, it isn't envisaged that this will introduce redundancy as the update time,
    description, and candidate annotation will be unique to that given peak.
    """

    def save(self, *args, **kwargs):
        """
        Method to override the save method of the Model superclass
        :param args:    Arguments passed to the method
        :param kwargs:  Keyword arguments passed to the method
        """

        # As before (see Compound.save()) the peak id is set at the creation of the instance.
        # However, the justification in this instance is because a peak does not have an intuitive name.
        if not self.id:
            peaks_in_fragmentation_set = Peak.objects.filter(fragmentation_set=self.fragmentation_set)
            peak_id_max = peaks_in_fragmentation_set.aggregate(Max('id'))['id__max']
            # Derive the highest peak id for all peaks within the fragmentation set
            if peak_id_max is None:
                peak_id_max = 0
            # The peak number will be one greater than the current max id
            peak_number = peak_id_max + 1
            """
            Note: Some identification of which fragmentation set the peak belongs to must
            be included in the slug. Otherwise if the creation of multiple fragmentation sets
            are ongoing concurrently the unique constraint of the slug field will be broken.
            """
            self.slug = slugify('Peak:' + str(peak_number) + 'FragSet:' + str(self.fragmentation_set.id))
        super(Peak, self).save(*args, **kwargs)

    def __unicode__(self):
        """
        Method to return a unicode representation of the Peak instance
        :return: String:    A sting specifying the 'id' of the peak
        """

        return 'Peak ' + str(self.id)


class CandidateAnnotation(models.Model):
    """
    A model to store the details of the candidate annotations. These are distinct from the compound model in
    that the information relates to how the reference spectra was measured and which peak it relates to.
    """

    compound = models.ForeignKey(Compound)
    peak = models.ForeignKey(Peak)
    # Although each spectral library returns a confidence value, these values are typically unique to each tool
    confidence = models.DecimalField(decimal_places=10, max_digits=20)
    annotation_query = models.ForeignKey(AnnotationQuery, null=True)
    # This is a boolean to denote whether the annotation is a close match by mass to the measured m/z of the peak
    mass_match = models.NullBooleanField(null=True)
    # The difference in m/z between the peak m/z and the mass returned by the annotation tool
    difference_from_peak_mass = models.DecimalField(decimal_places=10, max_digits=20, null=True)
    # Additional useful information such as the adduct, instrument type and collision energy are also stored
    adduct = models.CharField(max_length=500, null=True)
    instrument_type = models.CharField(max_length=500, null=True)
    collision_energy = models.CharField(max_length=500, null=True)
    # Additional information stores the full returned candidate annotation information for a spectral reference library
    # but may be used by other tools to provide relevant information
    additional_information = models.CharField(max_length=500, null=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        """
        Method to override the save method of the Model superclass
        :param args:    Arguments passed to the method
        :param kwargs:  Keyword arguments passed to the method
        """

        # As before in the Compound and Peak save methods, a candidate annotation does not have an intuitive
        # slug and therefore the next available id is used to identify it.
        if not self.id:
            annotations_in_query = CandidateAnnotation.objects.filter(annotation_query=self.annotation_query)
            annotation_id_max = annotations_in_query.aggregate(Max('id'))['id__max']
            if annotation_id_max is None:
                annotation_id_max = 0
            annotation_number = annotation_id_max + 1
            self.slug = slugify('Annotation:' + str(annotation_number) + 'Query:' + str(self.annotation_query.id))
        super(CandidateAnnotation, self).save(*args, **kwargs)

    def __unicode__(self):
        """
        Method to return a unicode representation of the CandidateAnnotation instance
        :return: String:    A string containing the annotation and the peak to which it is associated
        """

        return 'Annotation ' + str(self.id) + ' for Peak ' + str(self.peak.id)


class CompoundAnnotationTool (models.Model):
    """
    A model class to represent the origin of the compounds - i.e. which compound has been identified in which
    repository. However, it should be noted this is a Many-To-Many table as the same compound may be
    identified in many different spectral reference libraries.
    """

    compound = models.ForeignKey(Compound)
    annotation_tool = models.ForeignKey(AnnotationTool)
    # Store the unique reference used by the repository to identify the compound
    annotation_tool_identifier = models.CharField(max_length=500)

    def __unicode__(self):
        """
        Method to return a unicode representation of the CompoundAnnotation instance
        :return: String:    The Compound id and the AnnotationTool id are included.
        """

        return 'Compound ' + str(self.compound.id) + ' from AnnotationTool ' + str(self.annotation_tool.id)


class ExperimentalProtocol (models.Model):
    """
    A model class to represent the distinct experimental procedures implemented to generate the source files.
    For example GCMS-EII, LCMS-DDA, LCMS-DIA etc.
    """

    name = models.CharField(max_length=500)

    def __unicode__(self):
        """
        Method to return a unicode representation of the ExperimentalProtocol instance
        :return: String A string of the name of the experimental protocol
        """

        return self.name


class AnnotationToolProtocol (models.Model):
    """
    A model to represent the relationship between the AnnotationTools and the ExperimentalProtocols.
    Some of the developed AnnotationTools may, in future, be unsuitable for certain experimental protocols.
    """

    annotation_tool = models.ForeignKey(AnnotationTool)
    experimental_protocol = models.ForeignKey(ExperimentalProtocol)

    def __unicode__(self):
        """
        Method to return a unicode representation of an AnnotationToolProtocol instance
        :return: String:    A string containing the id of the AnnotationToolProtocol
        """

        return 'AnnotationToolProtocol' + str(self.id)


class AnnotationQueryHierarchy (models.Model):
    """
    A model representing the relationship between distinct AnnotationQueries
    """

    # An AnnotationQuery can be subqueried by specific AnnotationTools
    subquery_annotation_query = models.ForeignKey(AnnotationQuery, related_name="subquery")
    parent_annotation_query = models.ForeignKey(AnnotationQuery, related_name="parent_query")

    def __unicode__(self):
        """
        Method to return a unicode representation of an AnnotationQueryHierarchy
        :return: String: The word annotationqueryhierarchy concatinated with the id of the instance
        """

        return 'AnnotationQueryHierarchy' + str(self.id)

class PimpFrankPeakLink(models.Model):
    frank_peak = models.ForeignKey(Peak)
    pimp_peak = models.ForeignKey(PimpPeak,unique=True)

    def __unicode__(self):
        return "Pimp: {}, Frank: {}".format(self.pimp_peak.mass,self.frank_peak.mass)

class PimpProjectFrankExp(models.Model):

    #Model to link the PiMP project with a FrAnk Experiment
    pimp_project = models.ForeignKey(PimpProject, unique=True)
    frank_expt = models.ForeignKey(Experiment)

    def __unicode__(self):
        return self.pimp_project.title + "<-->" + self.frank_expt.title


class PimpAnalysisFrankFs(models.Model):
	# Object that links a PiMP analysis with a Frank fragmentation set
	pimp_analysis = models.ForeignKey(PimpAnalysis,unique=True)
	frank_fs = models.ForeignKey(FragmentationSet)
	status = models.CharField(max_length = 500)
	def __unicode__(self):
	    return  self.pimp_analysis.experiment.title + "<-->" + self.frank_fs.name