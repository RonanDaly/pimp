import numpy as np
import pandas as pd
import os
import collections
import logging

from sklearn import preprocessing
from collections import defaultdict

from experiments.models import Analysis, Parameter
from compound.models import Pathway
from data.models import Peak, PeakDTSample
from fileupload.models import Sample
from groups.models import Attribute

from pipeline_rpy2 import Rpy2PipelineMetadata
from helpers import convert_to_dataframe

logger = logging.getLogger(__name__)


class PlageAnalysis(object):

    # The constructor just takes in the analysis and defines the project
    def __init__(self, analysis):

        self.analysis = analysis
        self.project = Analysis.get_project(analysis)
        self.dataset = analysis.dataset_set.all()[0]

    """ Method to get setup and return the pathway activity dataframe
    :returns: Dataframe of pathways (rows), samples (columns) and the calulated activity from SVD
    """
    def get_plage_activity_df(self):

        int_df = self.construct_peak_int_df()
        self.standardize_intensity_df(int_df)
        plage_activity_df = self.calculate_pathway_activity_df(int_df)

        return plage_activity_df


    """A method to construct a peak_intestity dataframe with rows = peak_ids and columns = sample names
    Adapted from experiments.views.get_peak_table
    :returns: DF with index of peak Ids, columns of sample names and values of peak intensites.
    """
    def construct_peak_int_df(self):
        logger.info("Constructing the peak intensity DF")
        analysis = self.analysis
        comparisons = analysis.experiment.comparison_set.all()
        attributes = Attribute.objects.filter(comparison=comparisons).distinct().order_by('id')

        row_length = sum([len(a.sample.all()) for a in attributes])

        samples = Sample.objects.filter(
            attribute=attributes.distinct().order_by('attribute__id', 'id'))

        peakDTobjects = PeakDTSample.objects.filter(sample__in=samples, peak__dataset=self.dataset,
                                                    sample__attribute__in=attributes) \
            .select_related('peak', 'sample') \
            .distinct().order_by('peak__id', 'sample__attribute__id', 'sample__id')

        pp = map(list, zip(*[iter(peakDTobjects)] * row_length))

        # Create a list of lists of the peak table.
        # Peakgroup is all the samples belonging to a particular MS1 peak.
        pk_samp_intensities = []
        for peakgroup in pp:
            peak_int_list = []
            peak_int_list.append(peakgroup[0].peak.id)
            for peakdtsample in peakgroup:
                # Append the intensities of all the samples for this peak.
                peak_int_list.append(peakdtsample.intensity)
            pk_samp_intensities.append(peak_int_list)

        sample_fnames = [sample.name for sample in samples]

        int_df = pd.DataFrame(pk_samp_intensities).set_index([0])
        int_df.columns = sample_fnames
        int_df.index.name = "ms1_peak_id"
        int_df.columns.name = "sample_name"

        return int_df

    """Method to set the zero values in a DF and standardize across the samples
    :param: int_df: Dataframe of peak intensites (raw)
    :returns: DF with zero intensities replaced and the values standardized
    """
    def standardize_intensity_df(self, int_df):


        # Change the 0.00 intensities in the matrix to useable values
        np.array(self.change_zero_peak_ints(int_df))

        logger.info("Scaling the data across the sample: zero mean and unit variance")

        # standardize the data across the samples (zero mean and unit variance))
        scaled_data = preprocessing.scale(np.array(int_df), axis=1)
        # Put the scaled data back into df for further use
        sample_names = int_df.columns
        int_df[sample_names] = scaled_data

        # Standardizing, testing data
        mean = np.round(int_df.values.mean(axis=1))
        variance = np.round(int_df.values.std(axis=1))
        logger.info("Mean values of the rows in the DF is %s", str(mean))
        logger.info("Variance in the rows of the DF is %s", str(variance))

        return int_df

    """ Method to calculate the pathway activity DF given a dataframe of standardized intensities
    :param int_df: Takes in a standardized datframe (of peak intensites)
    :returns: A DF with Pathway names (rows) and the SVD activity levels for the samples (columns)
    """
    def calculate_pathway_activity_df(self, int_df):

        # Get all of the distinct pathways associated with this dataset
        pathways = Pathway.objects.filter(
            datasourcesuperpathway__compoundpathway__compound__peak__dataset=self.dataset).distinct()

        # For all of the pathways get all of the peak IDs
        pathway_activities = []
        for pw in pathways:
            peaks = Peak.objects.filter(compound__compoundpathway__pathway=pw, dataset=self.dataset)
            peak_ids = [p.id for p in peaks]
            pathway_peaks = int_df.ix[peak_ids]  # DF selected from peak IDs.
            w, d, c = np.linalg.svd(np.array(pathway_peaks))

            pw_act_list = []
            pw_act_list.append(pw.name)
            pw_act_list.extend(list(c[0]))

            pathway_activities.append(pw_act_list)

            activity_df = pd.DataFrame(pathway_activities).set_index([0])
            activity_df.columns = int_df.columns
            activity_df.index.name = "Pathways"

        return activity_df

    """ A method to change a 'zero' entries in a dataframe.
    If all intensities in a (factor) group are zero, a min value is set.
    If there are > 1 and < number in group zero intensities, then the average of the non_zeros entries is calculated
    and used. Assuming the PiMP mzXML file names are unique
    :param peak_int_df: A dataframe of peak intensities with peak ids (rows) and samples (columns)
    :returns: No return, modifies peak_int_df.
    """
    def change_zero_peak_ints(self, peak_int_df):

        # Get the min_intensity value set for the analysis
        logger.info("Setting the zero intensity values in the dataframe")
        min_intensity = float(Parameter.objects.get(params=self.analysis.params_id, name="minintensity").value)
        condition_group_dict = self.get_groups()
        # For each row of the intensities dataframe

        for idx, row in peak_int_df.iterrows():
            intensities = np.array(row.values)
            peak_id = idx
            # If there are any zero elements in the row
            zero_indices = np.where(intensities == 0)[0]

            # If a row has some zero indices
            if len(zero_indices) != 0:
                column_names = peak_int_df.columns[zero_indices].values
                zero_column_names = [c for c in column_names]

                for name, group in condition_group_dict.items():
                    # If all of the zero_columns are the indices of one group
                    if collections.Counter(zero_column_names) == collections.Counter(group):
                        # Set all the vales of the group to the minimum value
                        for z in zero_column_names:
                            peak_int_df.loc[peak_id, z] = min_intensity
                    # Else they are not all part of the group
                    else:
                        # Set the zero values in a group to the average of the non-zero values.
                        gp_ints = np.array([peak_int_df.loc[peak_id, g] for g in group if peak_int_df.loc[
                            peak_id, g] > 0])  # Array of all non-zero entries in the group
                        gp_mean = np.mean(gp_ints)
                        for g in group:
                            if peak_int_df.loc[peak_id, g] <= 0.0:  # If we have a zero value
                                peak_int_df.loc[peak_id, g] = gp_mean

    """ Method to return a dictionary of the groups (factors) and sample names
    (adapted from Joe's code)
    :returns:groups_dict: A dictionary of the group (key) and samples in that group (values) """
    def get_groups(self):

        m = Rpy2PipelineMetadata(self.analysis, self.project)
        groups, paths = m.get_groups()
        groups_df, _ = convert_to_dataframe(groups)

        groups_dict = defaultdict(list)
        for idx, row in groups_df.iterrows():
            values = row.values
            sample_name = values[0]
            file_name = paths[sample_name]
            factors = tuple(values[1:-1])
            groups_dict[factors].append(file_name)

        return groups_dict

