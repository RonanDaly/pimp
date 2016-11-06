__author__ = 'Scott Greig'

from frank.models import Peak, SampleFile, FragmentationSet, PimpFrankPeakLink, Experiment
from decimal import *
from abc import ABCMeta, abstractmethod
import rpy2.robjects as robjects
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.exceptions import ValidationError
from data.models import Peak as PimpPeak


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

    def __init__(self, r_dataframe, fragmentation_set_id, experiment_slug):
        """
        Constructor for the msnPeakBuilder. Validates all input required for the populating of peak database
        :param r_dataframe: The output of the R script (a dataframe). An rpy2.robjects dataframe.
        :param fragmentation_set_id: The unique database 'id' of the FragmentationSet to be populated
        :return: None
        """
        # Assume that this is not from Method 3 ar the start.
        self.from_method_3 = False

        # Ensure correct argument types are passed
        if r_dataframe is None or isinstance(r_dataframe, robjects.DataFrame) is False:
            raise TypeError('Invalid R dataframe - should be of type robjects.DataFrame')
        required_fields = ['peakID', 'MSnParentPeakID', 'msLevel', 'rt', 'mz', 'intensity', 'SourceFile']
        # Ensure dictionary keys (column names) of dataframe are correct
        for field in required_fields:
            if field not in r_dataframe.colnames:
                raise ValueError(
                    'Invalid R dataframe - column \'' + field + '\' is required'
                )
        # Ensure value of fragmentation set is valid
        try:
            self.fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except TypeError:
            raise

        # Extract the peak data from the R dataframe output
        self.peak_ID_vector = r_dataframe.rx2('peakID')
        self.parent_peak_id_vector = r_dataframe.rx2('MSnParentPeakID')
        self.msn_level_vector = r_dataframe.rx2('msLevel')
        self.retention_time_vector = r_dataframe.rx2('rt')
        self.mz_ratio_vector = r_dataframe.rx2('mz')
        self.intensity_vector = r_dataframe.rx2('intensity')

        self.experiment = Experiment.objects.get(slug=experiment_slug)

        # If we pass in pimpID as a row in the dataframe, it came from method 3
        if 'pimpID' in r_dataframe.colnames:
            # A vector to store the related pimp_peak IDs for pimp/frank integration.
            self.ms1_peak_id_vector = r_dataframe.rx2('pimpID')
            self.from_method_3 = True
            print("MS1 peaks came from Pimp")

        # sample_file_vector contains the 'name' (not filepath) of the source file from which the peak was derived
        # e.g. "Beer3_Top10_POS.mzXML"
        self.sample_file_vector = r_dataframe.rx2('SourceFile')
        if isinstance(self.sample_file_vector, robjects.FactorVector) is False:
            raise TypeError('Invalid R dataframe - SourceFile field should be Factor Vector')
        self.total_number_of_peaks = len(self.peak_ID_vector)
        if self.total_number_of_peaks <= 1:
            raise ValueError('No peaks were returned in R dataframe')
        # A dictionary used to store and match the corresponding allocated R id and a django model object
        # primary key id for each peak created
        self.created_peaks_dict = {}
        experiment = self.fragmentation_set.experiment
        # Limit the sample files to those in the experiment
        self.sample_files = SampleFile.objects.filter(sample__experimental_condition__experiment=experiment)

    def populate_database_peaks(self):
        """
        Method to populate the database peaks using the output of the R scripts
        which extract the peaks data from the mzXML files.
        :return: True:  Indicates that the database has been populated
        """

        print 'Populating database peaks...'
        # The starting index is the last element in the r_dataframe
        starting_index = self.total_number_of_peaks-1
        # Iterate through the peaks in reverse order
        for peak_array_index in range(starting_index, -1, -1):
            print 'Processing Peak: '+str(peak_array_index+1)+' of '+str(self.total_number_of_peaks)
            # Determine the peak id and the id of any precursor peak
            parent_peak_id = int(self.parent_peak_id_vector[peak_array_index])
            peak_id = int(self.peak_ID_vector[peak_array_index])
            # If the peak has a parent peak in the peak list and the product peak has yet been previously created
            existing_peak = False
            if peak_id in self.created_peaks_dict:
                existing_peak = True
            if parent_peak_id != 0 and existing_peak is False:
                # Obtain the database object for the parent ion
                try:
                    parent_peak_object = self._get_parent_peak(parent_peak_id)
                    self._create_a_peak(peak_array_index, parent_peak_object)
                except ValidationError:
                    raise

                    # # If the data comes from method 3
                    # if self.from_method_3:
                    #     # Link the parent peak object to the MS1 peak in Frank from which it came
                    #     self._link_frank_pimp_peaks()
                    #     print ('Finished linking peaks')

        # Else ignore the peak
        # Here peaks without any precursor ion are ignored, however,
        # the recursive method _get_parent_peak() will follow the hierarchy
        # of precursor ions, creating those that have fragments associated with them
        print 'This is from method 3' + str(self.from_method_3)

        print 'Finished populating peaks...'
        return True

    def _get_parent_peak(self, parent_id_from_r):
        """
        A recursive method to build a hierarchy of peaks from the leaf to root peak
        :param parent_id_from_r:    The numerical, R-assigned, id of the precursor peak
        :return: parent_peak_object:    The model object corresponding to the precursor peak
        """

        # If the precursor ion has been created previously, a reference will be in the dictionary
        if parent_id_from_r in self.created_peaks_dict:
            # Query the dictionary to retrieve the corresponding django primary key id
            # corresponding to the R peak id
            parent_django_id = self.created_peaks_dict.get(parent_id_from_r)
            # Retrieve the parent peak object from the database and return it
            parent_peak_object = Peak.objects.get(id=parent_django_id)
            return parent_peak_object
        else:
            # The parent peak object does not currently exist in the database
            # Obtain the array index of the precursor peak in the R ouput
            array_index_of_parent_ion = 0
            for peak_number in range(0, self.total_number_of_peaks):
                if int(self.peak_ID_vector[peak_number]) == parent_id_from_r:
                    array_index_of_parent_ion = peak_number
                    break
                if self.from_method_3:
                    pimp_id = self.ms1_peak_id_vector[array_index_of_parent_ion]

            # The parent_peak may itself have a precursor
            # Now the parent's precursor peak id used in the R dataframe can be derived
            parent_precursor_peak_id_in_r = int(self.parent_peak_id_vector[array_index_of_parent_ion])
            # Default is that the parent peak has no precursor itself
            precursor_peak_object = None
            if parent_precursor_peak_id_in_r != 0:
                # However, if the parent is itself a fragment this must be created in advance of the parent peak
                precursor_peak_object = self._get_parent_peak(parent_precursor_peak_id_in_r)
            # Finally, create the parent peak
            try:
                parent_peak_object = self._create_a_peak(array_index_of_parent_ion, precursor_peak_object)
            except ValidationError:
                raise
            return parent_peak_object

    def _create_a_peak(self, peak_array_index, parent_peak_object):
        """
        Method to add a peak to the database
        :param peak_array_index:    The index of the peak data in the R-dataframe to be added to the database
        :param parent_peak_object:  The parent peak object corresponding to the precursor ion of the peak to be created
        :return newly_created_peak: The created Peak model object
        """

        fragment_files = SampleFile.objects.filter(sample__experimental_condition__experiment=self.experiment)
        print "The fragment files are" + str(fragment_files)

        # If valid parameters then create the peak model instance
        sample_file_name = self.sample_file_vector.levels[self.sample_file_vector[peak_array_index] - 1]
        print "The sample file name is" + str(sample_file_name)
        peak_source_file = fragment_files.get(name=sample_file_name)
        peak_mass = self.mz_ratio_vector[peak_array_index]
        peak_retention_time = self.retention_time_vector[peak_array_index]
        peak_intensity = self.intensity_vector[peak_array_index]
        peak_msn_level = int(self.msn_level_vector[peak_array_index])

        print "peak level is" + str(peak_msn_level)
        if peak_msn_level == 1:
            print 'Parent peak and MS1 ID is:'
            ms1_id = self.ms1_peak_id_vector[peak_array_index]
            print ms1_id

        if peak_msn_level > 1:
            print 'not parent peak and MS1 ID is'
            print self.ms1_peak_id_vector[peak_array_index]

        try:
            newly_created_peak = Peak.objects.create(
                source_file=peak_source_file,
                mass=peak_mass,
                retention_time=peak_retention_time,
                intensity=peak_intensity,
                parent_peak=parent_peak_object,
                msn_level=peak_msn_level,
                fragmentation_set=self.fragmentation_set,
            )

            self.created_peaks_dict[int(self.peak_ID_vector[peak_array_index])] = newly_created_peak.id
            # If we have a parent peak link it back to Pimp
            if peak_msn_level == 1:
                print ("we are linking")
                self._link_frank_pimp_peaks(newly_created_peak, self.ms1_peak_id_vector[peak_array_index])

        except ValidationError:
            raise

        return newly_created_peak

    def _link_frank_pimp_peaks(self, frank_parent, pimp_ms1):

        ms1_peak = PimpPeak.objects.get(id=pimp_ms1)

        print ms1_peak.mass
        print ms1_peak.id
        print frank_parent.mass
        print frank_parent.id

        #     If a peak has an pimpID i.e it is not "None" .
        #     then this is an MS1 peak and should be linked directly to
        #     # a Pimp peak object

        pimp_frank_link = PimpFrankPeakLink.objects.create(pimp_peak=ms1_peak, frank_peak=frank_parent)
        print "The link is" + str(pimp_frank_link)


class GCMSPeakBuilder(PeakBuilder):
    """
    Class to populate gcms peaks into the database from an R generated text file
    """

    def __init__(self, output_file_list, fragmentation_set_id):
        """
        Constructor for the gcmsPeakBuilder
        :param output_file_list:    A String vector which is returned by are listing the filepaths for the source files
                                    the peaks are derived from.
        :param fragmentation_set_id:    An integer denoting the primary key of the fragmentation set to be populated
        :return True:   Indicates completion of the task
        """

        # Check the input parameters are valid
        # Ensure correct argument types are passed
        if output_file_list is None or isinstance(output_file_list, robjects.DataFrame) is False:
            raise TypeError('Invalid R dataframe - should be of type robjects.DataFrame')
        required_fields = ['mzXMLFiles', 'txtOutputFiles']
        # Ensure dictionary keys (column names) of dataframe are correct
        for field in required_fields:
            if field not in output_file_list.colnames:
                raise ValueError(
                    'Invalid R dataframe - column \'' + field + '\' is required'
                )
        # Ensure value of fragmentation set is valid
        try:
            self.fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except TypeError:
            raise
        # Extract the filepaths of the source mzXML and text output files
        self.source_files_vector = output_file_list.rx2('mzXMLFiles')
        if isinstance(self.source_files_vector, robjects.FactorVector) is False:
            raise TypeError('Invalid R dataframe - mzXMLFiles field should be Factor Vector')
        self.peak_list_files_vector = output_file_list.rx2('txtOutputFiles')
        if isinstance(self.peak_list_files_vector, robjects.FactorVector) is False:
            raise TypeError('Invalid R dataframe - txtOutputFiles field should be Factor Vector')
        # Ensure the R Script has returned peaks to be populated
        self.number_of_source_files = len(self.source_files_vector)
        if self.number_of_source_files < 1:
            raise ValueError('No peaks to populate')

    def populate_database_peaks(self):
        """
        Method to populate gcms peaks from a R generated Text file
        :return: True:  Indicator of completion of the population of the peaks
        """

        print 'Populating Database peaks...'
        print 'Number of source files = ' + str(self.number_of_source_files)
        for index in range(0, self.number_of_source_files):
            # Index must be decreased by 1 due to the indexing used in R (starts at 1, not the conventional 0)
            directory_of_mzxml_file = self.source_files_vector.levels[self.source_files_vector[index] - 1]
            print 'Processing Peaks From ' + directory_of_mzxml_file
            directory_of_output_txt_file = self.peak_list_files_vector.levels[self.peak_list_files_vector[index] - 1]
            # Group the peaks into a dictionary
            try:
                grouped_peaks = self._group_peaks(directory_of_output_txt_file, directory_of_mzxml_file)
            except IOError:
                raise
            except ValueError:
                raise
            except InvalidOperation:
                raise
            except MultipleObjectsReturned:
                raise
            except ObjectDoesNotExist:
                raise
            # Add the derived peaks to the database
            try:
                self._add_peaks_to_database(grouped_peaks)
            except ValidationError:
                raise
        print 'Peaks Populated'
        return True

    def _group_peaks(self, file_directory, source_directory):
        """
        Method to extract the peak data from a Text file and group the peaks into a python dictionary
        :param file_directory:  The directory of the text file containing the peak data
        :param source_directory:    The directory of the source file (the mzXML file)
                                    from which the peaks are derived from
        :return: peak_dictionary:   A dictionary of the peaks grouped by their relation.id
        """

        peak_dictionary = {}
        # Try to retrieve the source_file object
        try:
            source_file_object = SampleFile.objects.get(address=source_directory)
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        # Try to retrive the peak data from the source file
        input_file = None
        try:
            with open(file_directory, "r") as input_file:
                current_group_id = -1
                # An initial default value to ensure initial peak dictionary group is correctly initialised
                for line in input_file:
                    # We are only interested in the lines which begin with a peak id
                    if line[0].isdigit():
                        # Data elements are delimited by tabs
                        line_tokens = line.split('\t')
                        # The tokens are extracted containing the peak data
                        try:
                            peak_mass = Decimal(line_tokens[1])
                            peak_retention_time = Decimal(line_tokens[2])
                            peak_intensity = Decimal(line_tokens[3])
                            peak_relation_id = int(line_tokens[4])
                        except ValueError:
                            raise
                        except InvalidOperation:
                            raise
                        # Create a new peak object, however, this should not be commited to the database
                        # until the correct precursor ion has been allocated to the peak
                        new_peak = Peak(
                            source_file=source_file_object,
                            mass=peak_mass,
                            retention_time=peak_retention_time,
                            intensity=peak_intensity,
                            parent_peak=None,
                            msn_level=2,
                            fragmentation_set=self.fragmentation_set,
                        )
                        # If the relation_id of the peak does not belong to the current grouping, create a new group
                        # in the dictionary
                        if current_group_id != peak_relation_id:
                            current_group_id = peak_relation_id
                            peak_dictionary[peak_relation_id] = []
                        # Finally, add the new peak object to the created_peaks dictionary
                        peak_dictionary[peak_relation_id].append(new_peak)
        except IOError:
            raise
        finally:
            # Using 'with' should close the file but make sure
            if input_file.closed is False:
                input_file.close()
        return peak_dictionary

    def _add_peaks_to_database(self, grouped_peaks):
        """
        Method to add the peaks to the database in their correct groupings
        :param grouped_peaks: A dictionary containing all of the peaks to be added to the database, grouped by
                                their relation.id
        :return True:   Boolean indicates that the peaks have been successfully added to the database
        """

        for relation in grouped_peaks:
            most_intense_peak = grouped_peaks[relation][0]
            # By default, set the most intense peak to be the first peak in the group
            for peak in grouped_peaks[relation]:
                if peak.intensity > most_intense_peak.intensity:
                    most_intense_peak = peak
            # Identify the peak with the greatest intensity - this is the pseudo-ms1 peak
            try:
                pseudo_ms1_peak = Peak.objects.create(
                    source_file=most_intense_peak.source_file,
                    mass=most_intense_peak.mass,
                    retention_time=most_intense_peak.retention_time,
                    intensity=most_intense_peak.intensity,
                    parent_peak=None,
                    msn_level=1,
                    fragmentation_set=self.fragmentation_set,
                )
                for peak in grouped_peaks[relation]:
                    peak.parent_peak = pseudo_ms1_peak
                    peak.save()
            except ValidationError:
                raise
        return True
