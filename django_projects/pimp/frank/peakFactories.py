__author__ = 'Scott Greig'

from frank.models import Peak, SampleFile, FragmentationSet, PimpFrankPeakLink, Experiment
from decimal import *
from abc import ABCMeta, abstractmethod
import rpy2.robjects as robjects
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from data.models import Peak as PimpPeak
import sys
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

class PeakBuilder:
    """
    Abstract class to for all classes which are required to populate the database of the peaks
    derived from the various R scripts used.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def populate_database_peaks(self):
        """
        Abstract method to populate the database of peaks from the R script outputs
        :return:Error   Method is not instantiated
        """

        raise NotImplementedError('Subclass must instantiate populate_database_peaks(self)')


class MSNPeakBuilder(PeakBuilder):
    """
    Class defining a tool for extracting msn peaks from the lcms-msn dataset
    output from Tony Lawson's R script.
    Inherits from the Abstract PeakBuilder class
    """

    def __init__(self, output, fragmentation_set_id, experiment_slug):
        """
        Constructor for the msnPeakBuilder. Validates all input required for the populating of peak database
        :param output: The output of the fragfile_extraction script: ms1: list of ms1 objetcs, ms2 list of tuples
        and for a particular one, the third value is a reference to the corresponding ms1 and some metadata.
        :param fragmentation_set_id: The unique database 'id' of the FragmentationSet to be populated
        :return: None
        """
        self.ms1, self.ms2, self.metadata = output
        # Assume that this is not from Method 3 ar the start.
        self.from_pimp = False

        logger.info("We have {} MS1 and {} MS2 peaks".format(len(self.ms1), len(self.ms2)))

        # Ensure correct argument types are passed
        if (len(self.ms1) == 0) or (len(self.ms2) == 0) or (len(self.metadata) == 0):
            raise ValueError('No peaks were returned in by fragfile_extraction.py')

        # Ensure value of fragmentation set is valid
        try:
            self.fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except TypeError:
            raise

        self.experiment = Experiment.objects.get(slug=experiment_slug)

        # A dictionary used to store and match the corresponding ms1 peak from the fragfile_extraction
        #  and a django model object primary key id for each FrAnK peak created
        self.ms1obj_frankpeak_dict = {}
        experiment = self.fragmentation_set.experiment

        # Limit the sample files to those in the experiment
        self.sample_files = SampleFile.objects.filter(sample__experimental_condition__experiment=experiment)
        logger.info("Finished initalising the peakbuilder")

    def populate_database_peaks(self):
        """
        Method to populate the database peaks using the output of fragfile_extration code
        which extract the peaks data from the mzML files.
        :return: True:  Indicates that the database has been populated
        """

        logger.info('Populating database peaks...')
        logger.info("Initially, populating the MS1 Peak tables in FrAnk")
        for ms1_object in self.ms1:
                try:
                    self._create_ms1_peak(ms1_object)
                except Exception:
                    logger.warning("Can't create this MS1 peak")
                    raise

        logger.info("...and now populating the MS2 Peak tables in FrAnk")
        for ms2_tuple in self.ms2:
                try:
                    self._create_ms2_peak_objects(ms2_tuple)
                except Exception:
                    logger.warning("Can't create this MS2 peak")
                    raise

        # This can be added once the slugs are removed from FrAnK
        # for ms2_tuple in self.ms2:
        #     try:
        #         peak_objects = self._create_ms2_peak_objects(ms2_tuple)
        #     except Exception:
        #         raise
        #
        # try:
        #     logger.info("Bulk creating the MS2 Peak objects")
        #     #Peak.objects.bulk_create(peak_objects)
        # except Exception:
        #     raise

        logger.info('Finished populating peaks...')

        return True

    def _create_ms1_peak(self, ms1_peak_object):
        """
        Method that creates an MS1 peak in the DB
        :param ms1_peak_object:   An MS1 peak object returned from processing of the fragmentation files.
        :return newly_created_peak: The created MS1 Peak model object
        """
        fragment_files = SampleFile.objects.filter(sample__experimental_condition__experiment=self.experiment)
        pimp_id = ms1_peak_object.pimp_id

        # If valid parameters then create the peak model instance
        sample_file_name = ms1_peak_object.file_name
        print 'sample_file_name ', sample_file_name
        peak_source_file = fragment_files.get(name=sample_file_name)

        peak_mass = ms1_peak_object.mz
        peak_retention_time = ms1_peak_object.rt
        peak_intensity = ms1_peak_object.intensity
        peak_msn_level = 1

        try:
            newly_created_peak = Peak.objects.create(
                source_file=peak_source_file,
                mass=peak_mass,
                retention_time=peak_retention_time,
                intensity=peak_intensity,
                msn_level=peak_msn_level,
                fragmentation_set=self.fragmentation_set,
            )

            #Link between the MS1 peak object returned from fragfile_extration and this frank Peak
            self.ms1obj_frankpeak_dict[ms1_peak_object.id] = newly_created_peak.id

            #  If the MS1 peaks came from PimP create a link between Pimp and Frank
            if pimp_id is not None:
                    self.link_frank_pimp_peaks(newly_created_peak, pimp_id)

        except Exception:
            logger.error("create MS1 failed")
            raise

        return newly_created_peak

    def _create_ms2_peak_objects(self, ms2_tuple):

        """
        This method is kept separate from the MS1 peak creation as it is designed to populate the DB in batch.
        This is not possible with the MS1 peaks as an entry to the ms1obj_frankpeak_dict is amended each time an MS1 peak is created.
        :param ms2_tuple: A tuple entry from the list of ms2 tuples returned from fragfile_extraction.
        :return: list of peak objects to be populated in the DB
        """
        #The MS2 tuple contains: mz ([0]), current_ms1_rt ([1]), ms2_intensity ([3]), related ms1 object, file_name ([4]), ms2_id(float)

        fragment_files = SampleFile.objects.filter(sample__experimental_condition__experiment=self.experiment)

        # If valid parameters then create the peak model instance
        sample_file_name = ms2_tuple[4]
        peak_source_file = fragment_files.get(name=sample_file_name)

        peak_mass = ms2_tuple[0]
        peak_retention_time = ms2_tuple[1]
        peak_intensity = ms2_tuple[2]
        peak_msn_level = 2

        #Get the parent peak (MS1) object
        related_ms1 = ms2_tuple[3]
        ms1_peak_id = self.ms1obj_frankpeak_dict[related_ms1.id]
        ms1_peak = Peak.objects.get(id=ms1_peak_id)

        try:
            Peak.objects.create(
                source_file=peak_source_file,
                mass=peak_mass,
                retention_time=peak_retention_time,
                intensity=peak_intensity,
                msn_level=peak_msn_level,
                fragmentation_set=self.fragmentation_set,
                parent_peak=ms1_peak,
            )
        except Exception:
            logger.error("create MS2 failed")
            raise

        #This can be used once the slugs are removed from FrAnK
        # peak_objects = [
        #     Peak(
        #         source_file=peak_source_file,
        #         mass=peak_mass,
        #         retention_time=peak_retention_time,
        #         intensity=peak_intensity,
        #         msn_level=peak_msn_level,
        #         fragmentation_set=self.fragmentation_set,
        #         parent_peak=ms1_peak,
        #     )
        # ]
        #return peak_objects

    def link_frank_pimp_peaks(self, frank_parent, pimp_ms1):

        ms1_peak = PimpPeak.objects.get(id=pimp_ms1)

        #Create a link if itdoesn't already exist.
        pimp_frank_link = PimpFrankPeakLink.objects.get_or_create(pimp_peak=ms1_peak, frank_peak=frank_parent)
