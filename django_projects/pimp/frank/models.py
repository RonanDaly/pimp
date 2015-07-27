from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
import os
from pimp.settings_dev import MEDIA_ROOT
import hashlib

# The default Django User model provides the following attributes:
#	username
#	password
#	email
#	first_name
#	last_name

# A tuple containing the file 'types' ie. the polarity of the file
FILE_TYPES = (
    ('Positive', 'Positive'),
    ('Negative', 'Negative'),
)

# A tuple containing the 'state' of the analysis to provide the user with feedback
ANALYSIS_STATUS = (
    ('Submitted', 'Submitted'),
    ('Processing', 'Processing'),
    ('Completed Successfully', 'Completed Successfully'),
    ('Completed with Errors', 'Completed with Errors'),
)

# Define the choices for ionisation protocol
IONISATION_PROTOCOLS = (
    ('EIS','Electron Ionisation Spray'),
    # Additional ionisation protocols could be added here if necessary
)

# Define the choices for method of detection, dictates method of how peaks are derived
DETECTION_PROTOCOLS = (
    ('LCMS DDA','Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'),
    ('LCMS DIA', 'Liquid-Chromatography Data-Independent Acquisition'),
    ('GCMS EII','Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation'),
)

# Class defining the experiments created by the users
class Experiment(models.Model):
    title = models.CharField(max_length = 250, blank = False)
    description = models.CharField(max_length = 250)
    created_by = models.ForeignKey(User, related_name = "experiment_creator")
    time_created = models.DateTimeField(auto_now = True)
    last_modified = models.DateTimeField(auto_now_add = True, blank = True)
    ionisation_method = models.CharField(max_length = 250, choices = IONISATION_PROTOCOLS)
    detection_method = models.CharField(max_length = 250, choices = DETECTION_PROTOCOLS)
    users = models.ManyToManyField(User, through = 'UserExperiments', through_fields = ('experiment', 'user'))
    slug = models.SlugField(unique=True)

    # Upon saving an instance of the model, a unique slug is derived for referencing in the URL
    def save(self, *args, **kwargs):
        ## The experiment id is going to be one greater than the total number of existing experiments in the database.
        experiment_number = Experiment.objects.count()+1
        # The slug is simply the experiment title plus the next available index
        self.slug = slugify(self.title)+'-'+str(experiment_number)
        super(Experiment, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Experiment '+str(self.id)+': '+self.title

## Class defining the many-to-many relationships between a user and experiments
class UserExperiments(models.Model):
    user = models.ForeignKey(User)
    experiment = models.ForeignKey(Experiment)

    def __unicode__(self):
        return self.user.username +' access to '+self.experiment.title

# Class to define the experimental conditions of an experiment
class ExperimentalCondition(models.Model):
    name = models.CharField(max_length = 250, blank = False)
    description = models.CharField(max_length = 250)
    experiment = models.ForeignKey(Experiment)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        ## The id is going to be one greater than the total number of existing experimentalConditions in the database.
        condition_number = ExperimentalCondition.objects.count()+1
        # The slug is simply the name of the experimental condition and the next available index
        self.slug = slugify(self.name)+'-'+str(condition_number)
        super(ExperimentalCondition, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name+' in '+self.experiment.title

# Class to define the samples which may be included in each experimental condition
class Sample(models.Model):
    name = models.CharField(max_length = 250, blank = False)
    description = models.CharField(max_length = 250, blank = False)
    experimental_condition = models.ForeignKey(ExperimentalCondition)
    organism = models.CharField(max_length = 250)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        ## The sample id is going to be one greater than the total number of existing samples in the database.
        sample_number = Sample.objects.count()+1
        # The slug is simply the concatination of the name of the sample and the next available id
        self.slug = slugify(self.name)+'-'+str(sample_number)
        super(Sample, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Sample '+str(self.id)+ ' in '+ self.experimental_condition.experiment.title


# Method to generate the absolute directory of the uploaded file
def get_upload_file_name(instance, filename):
    # Retrive the sample, experimental condition and experiment to which the sample file is to be associated
    sample_object = instance.sample
    experimental_condition_object = sample_object.experimental_condition
    experiment_object = experimental_condition_object.experiment
    # The directory of the file upload is concatinated to the root directory
    filepath = os.path.join(MEDIA_ROOT,
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
            # Directory already exists
            pass
    # Finally, the filename is contatinated to the directory
    upload_location = os.path.join(filepath, filename)
    return upload_location
    ## Remember to fix the problem that if two identical files are added to the same experiment
    ## then Django will create a duplicate file in the directory
    ## Should probably be done in the form.

# Class corresponding to the sampke files corresponding to the sample
class SampleFile(models.Model):
    name = models.CharField(max_length = 250, blank = False)
    polarity = models.CharField(max_length = 250, choices = FILE_TYPES)
    sample = models.ForeignKey(Sample, blank = False)
    address = models.FileField(upload_to = get_upload_file_name)

    def __unicode__(self):
         return self.name

# Class defining a Fragmentation Set of an Experiment - i.e. a collection of peaks
class FragmentationSet(models.Model):
    name = models.CharField(max_length = 250)
    experiment = models.ForeignKey(Experiment)
    time_created = models.DateTimeField(auto_now = True)
    status = models.CharField(max_length = 250, choices = ANALYSIS_STATUS, default='Submitted')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        ## The fragmentation set id is going to be one greater than the total number of existing sets in the database.
        set_number = FragmentationSet.objects.count()+1
        # The slug is simply the concatination of the name of the fragmentation set and the next available id
        self.slug = slugify(self.name)+'-'+str(set_number)
        super(FragmentationSet, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Fragmentation Set '+str(self.id)

# Class defining an Annotation Query - i.e. a collection of candidate annotations
class AnnotationQuery(models.Model):
    name = models.CharField(max_length = 250)
    fragmentation_set = models.ForeignKey(FragmentationSet)
    time_created = models.DateTimeField(auto_now = True)
    status = models.CharField(max_length = 250, choices = ANALYSIS_STATUS, default='Defined')
    slug = models.SlugField(unique=True)
    massBank = models.BooleanField(default = False)
    nist = models.BooleanField(default = False)
    massBank_params = models.CharField(max_length = 250, null=True)
    ### Note additional parameters required here ####
    ### Also need to add in the choice field for Simon's additional code
    parent_annotation_query = models.ForeignKey('self', null=True)

    def save(self, *args, **kwargs):
        ## The query id is going to be one greater than the total number of existing queries in the database.
        query_number = AnnotationQuery.objects.count()+1
        # The slug is simply the concatination of the name of the query and the next available id
        self.slug = slugify(self.name)+'-'+str(query_number)
        super(AnnotationQuery, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Annotation Query '+str(self.id)

# Class defining the respositories which are queried during an analysis
class Repository (models.Model):
    name = models.CharField(max_length = 250, blank = False)

    def __unicode__(self):
        return self.name

# Class defining the compounds identified from the repositories
class Compound(models.Model):
    name = models.CharField(max_length=500)
    formula = models.CharField(max_length = 250)
    exact_mass = models.DecimalField(decimal_places=10, max_digits=20)
    inchikey = models.CharField(max_length=500, null=True)
    repository = models.ManyToManyField(Repository, through = 'CompoundRepository')

    def __unicode__(self):
        return self.formula


# Class defining the peaks derived from the source files
class Peak(models.Model):
    source_file = models.ForeignKey(SampleFile, blank = False)
    mass = models.DecimalField(decimal_places = 10, max_digits = 20)
    retention_time = models.DecimalField(decimal_places = 10, max_digits = 20)
    intensity = models.DecimalField(decimal_places = 10, max_digits = 20)
    parent_peak = models.ForeignKey('self', null=True)
    msn_level = models.IntegerField(default = 0)
    annotations = models.ManyToManyField(Compound, through = 'CandidateAnnotation')
    fragmentation_set = models.ForeignKey(FragmentationSet)
    slug = models.SlugField(unique=True)
    preferred_candidate_annotation = models.ForeignKey(AnnotationQuery, null=True)
    preferred_candidate_description = models.CharField(max_length = 250, null=True)
    preferred_candidate_user_selector = models.ForeignKey(User, null=True)
    preferred_candidate_updated_date = models.DateTimeField(auto_now_add = True, blank = True)

    def save(self, *args, **kwargs):
        peak_number = Peak.objects.count()+1
        # The slug has to contain both the peak number and the fragmentation set number to ensure slug field
        # remains unique throughout celery processes
        self.slug = slugify('Peak:'+str(peak_number)+'FS:'+str(self.fragmentation_set.id))
        super(Peak, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Peak '+str(self.id)

# Class defining the candidate annotations which are assigned to peaks
class CandidateAnnotation(models.Model):
    compound = models.ForeignKey(Compound)
    peak = models.ForeignKey(Peak)
    confidence = models.DecimalField(decimal_places = 10, max_digits = 20)
    annotation_query = models.ForeignKey(AnnotationQuery, null=True)
    mass_match = models.NullBooleanField(null=True)
    difference_from_peak_mass = models.DecimalField(decimal_places = 10, max_digits = 20, null=True)
    adduct = models.CharField(max_length=500, null=True)
    instrument_type = models.CharField(max_length=500, null=True)
    collision_energy = models.CharField(max_length=500, null=True)
    additional_information = models.CharField(max_length=500, null=True)

    def __unicode__(self):
        return 'Annotation '+str(self.id)+' for Peak '+str(self.peak.id)

# Class defining which compounds were identified in which repositories
class CompoundRepository (models.Model):
    compound = models.ForeignKey(Compound)
    repository = models.ForeignKey(Repository)
    # Store the reference used by the repository to identify the compound
    repository_identifier = models.CharField(max_length=500)

    def __unicode__(self):
        return 'Compound '+str(self.compound.id)+' from Repository '+str(self.repository.id)