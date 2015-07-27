##### File containing classes which assist in the deriving of peaks from mzXML files ######

from frank.models import Peak, SampleFile, FragmentationSet, Experiment, ExperimentalCondition, Sample

## Class to derive those peaks which have an associated fragmentation spectrum from
## LC-MSN data sets
class msnPeakBuilder:
    def __init__(self, r_dataframe, fragmentation_set_id):
        # Vector of the 'R' allocated ids of the peaks
        self.peak_ID_vector = r_dataframe[0]
        self.parent_peak_id_vector = r_dataframe[1]
        self.msn_level_vector = r_dataframe[2]
        self.retention_time_vector = r_dataframe[3]
        self.mz_ratio_vector = r_dataframe[4]
        self.intensity_vector = r_dataframe[5]
        # sample_file_vector contains the 'name' of the source file from which the peak was derived
        # e.g. "Beer3_Top10_POS.mzXML"
        self.sample_file_vector = r_dataframe[9]
        # The total number of peaks is simple the number of rows in the dataframe
        self.total_number_of_peaks = len(self.peak_ID_vector)
        # A dictionary to record the association of the R assigned id and the new django primary key id
        # for each peak created
        self.created_peaks_dict = {}
        self.fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
        # Limit the sample files to those in the experiment
        experiment = self.fragmentation_set.experiment
        self.sample_files = SampleFile.objects.filter(sample__experimental_condition__experiment=experiment)

    # Method to iterate through all the MSN peaks adding those peaks with associated fragmentation
    # spectra to the database
    def populate_database_peaks(self):
        print 'Populating database peaks...'
        starting_index = self.total_number_of_peaks-1
        # Iterate through the peaks in reverse order
        for peak_array_index in range(starting_index, 0, -1):
            # Determine whether there is a parent peak
            parent_peak_id = int(self.parent_peak_id_vector[peak_array_index])
            peak_id = int(self.peak_ID_vector[peak_array_index])
            # If there is a parent peak and peak has not been previously created
            existing_peak = False
            if peak_id in self.created_peaks_dict:
                existing_peak = True
            if parent_peak_id != 0 and existing_peak is False:
                # Obtain the database object for the parent ion
                parent_peak_object = self.getParentPeak(parent_peak_id)
                self.createAPeak(peak_array_index, parent_peak_object)
        # Else ignore the peak
        # Here peaks without any precursor ion are ignored, however,
        # the recursive method makeParentPeak() will follow the hierarchy
        # of precursor ions, creating those that have fragments associated with them
        print 'Finished populating peaks...'

    # Method to obtain the parent peak of the precursor peak
    def getParentPeak(self, parent_id_from_r):
        # If the parent ion has been created previously, a reference will be in the dictionary
        if parent_id_from_r in self.created_peaks_dict:
            # Query the dictionary to retrieve the corresponding django reference
            parent_django_id = self.created_peaks_dict.get(parent_id_from_r)
            # Retrieve the parent peak object from the database and return it
            parent_peak_object = Peak.objects.get(id=parent_django_id)
            return parent_peak_object
        else: # The parent peak object does not currently exist in the database
            # In the case of MSN data, the parent ion itself may have a precursor
            # Firstly, we need the array index of the parent ion's data
            array_index_of_parent_ion = 0
            for peak_number in range(0, self.total_number_of_peaks):
                if int(self.peak_ID_vector[peak_number]) == parent_id_from_r:
                    array_index_of_parent_ion = peak_number
                    break
            # Now the parent's precursor peak id used in the R dataframe can be derived
            parent_precursor_peak_id_in_r = int(self.parent_peak_id_vector[array_index_of_parent_ion])
            # Default is that the parent has no precursor
            precursor_peak_object = None
            if parent_precursor_peak_id_in_r != 0:
                # However, if a parent exists this may have to be created in advance - recursive call
                precursor_peak_object = self.getParentPeak(parent_precursor_peak_id_in_r)
            # Lastly, create the parent peak
            created_parent_ion = self.createAPeak(array_index_of_parent_ion, precursor_peak_object)
            return created_parent_ion

    # Method to add a peak to the database
    def createAPeak(self, peak_array_index, parent_peak_object):
        sample_file_name = self.sample_file_vector.levels[self.sample_file_vector[peak_array_index]-1]
        peak_source_file = self.sample_files.get(name=sample_file_name)
        peak_mass = self.mz_ratio_vector[peak_array_index]
        peak_retention_time = self.retention_time_vector[peak_array_index]
        peak_intensity = self.intensity_vector[peak_array_index]
        peak_msn_level = int(self.msn_level_vector[peak_array_index])
        newly_created_peak = Peak.objects.create(
                source_file = peak_source_file,
                mass = peak_mass,
                retention_time = peak_retention_time,
                intensity = peak_intensity,
                parent_peak = parent_peak_object,
                msn_level = peak_msn_level,
                fragmentation_set = self.fragmentation_set,
        )
        self.created_peaks_dict[int(self.peak_ID_vector[peak_array_index])] = newly_created_peak.id
        return newly_created_peak