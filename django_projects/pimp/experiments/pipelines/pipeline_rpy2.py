import multiprocessing
import os
import re
import shutil

from django.conf import settings
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

from experiments.models import Comparison, Database
from fileupload.models import Sample, Picture, CalibrationSample
from groups.models import Group
import numpy as np
import pandas as pd
from pimp.settings import getString, getNeededString
import rpy2.robjects as robjects

import logging

logger = logging.getLogger(__name__)

class Rpy2Pipeline(object):
    """
    New pipeline entirely controlled from Python

    TODO: remove all database calls from the R side. Many methods in setup() can be pythonised.
    TODO: include blanks (and qc?) during the data processing too!!
    TODO: generate_combinations() needlessly complex??
    TODO: do we need a new Factor class?
    """

    # read and think about this:
    # http://stackoverflow.com/questions/5707382/is-multiprocessing-with-rpy-safe
    def __init__(self, analysis, project, saveFixtures):

        self.connect_to_rpy2()

        self.analysis = analysis
        self.project = project
        self.saveFixtures = saveFixtures
        self.metadata = Rpy2PipelineMetadata(analysis, project)

        self.setup()

    def connect_to_rpy2(self):

        logger.info('******************************************')
        logger.info('Setup rpy2 connection')
        logger.info('******************************************')

        packrat_lib_path = self.get_env_packrat_lib_path()
        set_lib_path = robjects.r['.libPaths']
        set_lib_path(packrat_lib_path)

        base = importr('base')
        base.options(**{'java.parameters':"".join(["-Xmx",str(1024*8),"m"])})
        importr('PiMP')

        # activate the conversion from pandas dataframe to r
        pandas2ri.activate()

    def setup(self):

        self.working_dir = self.get_pimp_wd(self.project.id)
        self.validate_input()
        pp = self.get_analysis_params(self.analysis.id)
        self.pimp_params = self.create_analysis_dir(self.analysis.id, pp)

        # generate std xml
        stds = robjects.StrVector(self.metadata.stds)
        databases = robjects.StrVector(self.metadata.databases)
        generate_std_xml = robjects.r('Pimp.generateStdXml')
        output = generate_std_xml(stds, databases, self.pimp_params, self.working_dir)
        self.r_dbs = output[output.names.index('DBS')]
        self.r_databases = output[output.names.index('databases')]

    def get_pimp_wd(self, project_id):

        base_dir = getNeededString('PIMP_BASE_DIR')
        defined_media_root = os.path.join(base_dir, '..', 'pimp_data')
        media_root = getString('PIMP_MEDIA_ROOT', defined_media_root)
        data_dir = os.path.join(media_root, 'projects')
        project_dir = os.path.join(data_dir, str(project_id))

        logger.info('Data dir: %s', data_dir)
        logger.info('Project dir: %s', project_dir)

        return project_dir

    def validate_input(self):

        pos_files = self.metadata.files['positive']
        neg_files = self.metadata.files['negative']
        all_files = list(pos_files)
        all_files.extend(neg_files)
        logger.debug('all_files %s', all_files)
        logger.debug('working_dir %s', self.working_dir)

        # check that all the input files are there
        for f_name in all_files:
            f_path = os.path.join(self.working_dir, f_name)
            assert os.path.isfile(f_path)

        # validate that pos and neg files are of the same length and are consistent
        assert len(pos_files) == len(neg_files)
        for f in range(len(pos_files)):
            pos = os.path.basename(pos_files[f])
            neg = os.path.basename(neg_files[f])
            assert pos == neg

    def get_analysis_params(self, analysis_id):
        get_analysis_params = robjects.r['Pimp.getAnalysisParams']
        pimp_params = get_analysis_params(analysis_id)
        return pimp_params

    def create_analysis_dir(self, analysis_id, pimp_params):
        create_analysis_dir = robjects.r['Pimp.createAnalysisDir']
        # pimp_params$mzmatch.outputs will be updated inside to point to the right analysis folder
        pimp_params = create_analysis_dir(analysis_id, pimp_params, self.working_dir)
        return pimp_params

    ############################################################
    # pipeline methods to process raw data
    ############################################################

    def process_raw_data(self, polarity, xcms_params, mzmatch_params,
                         peakml_params, mzmatch_outputs, mzmatch_filters, n_slaves):

        format_mzmatch_outputs = robjects.r['Pimp.getFormattedMzmatchOutputs']
        formatted_mzmatch_outputs = format_mzmatch_outputs(self.analysis.id, polarity, mzmatch_outputs)
        polarity_dir, combined_dir = self.create_input_directories(polarity, formatted_mzmatch_outputs)

        logger.info('------------------------------------------')
        logger.info('%s %s %s', polarity, polarity_dir, combined_dir)
        logger.info('------------------------------------------')

        # peak detection and rt correction
        self.create_peakml(polarity, polarity_dir, xcms_params, mzmatch_params,
                           peakml_params, mzmatch_outputs, n_slaves)

        # separate samples into peaksets for grouping
        r_combi = self.generate_peaksets(polarity, polarity_dir, combined_dir, mzmatch_params)

        # filter each peakset
        peaksets = self.filter_peaksets(combined_dir, mzmatch_params)

        # combine peaksets into a single peakml file and filter it
        out_file = self.combine_final(polarity, peaksets, mzmatch_params, formatted_mzmatch_outputs)
        out_file = self.filter_final(polarity, out_file, mzmatch_filters, mzmatch_params, formatted_mzmatch_outputs)

        # do gap filling
        out_file = self.gap_filling(polarity, out_file, peakml_params, formatted_mzmatch_outputs)

        # do related peaks
        out_file, basepeak_file = self.related_peaks(polarity, out_file, mzmatch_params, formatted_mzmatch_outputs)

        # do identification
        databases = self.r_dbs
        groups = r_combi
        raw_data = self.identify(polarity, out_file, databases, groups, mzmatch_params, formatted_mzmatch_outputs)
        return raw_data, r_combi

    def convert_to_dataframe(self, factors):

        # get unique samples (files) in sorted order
        all_files = set()
        for f in factors:
            for lev in f.levels:
                lev_files = f.level_files[lev]
                all_files.update(lev_files)
        all_files = sorted(list(all_files))

        # get the levels for each sample
        sample_levels = {}
        for sample in all_files:
            sample_levels[sample] = []

        for sample in all_files:
            for factor in factors:
                val = factor.get_level(sample)
                sample_levels[sample].append(val)

        # construct the dataframe
        data = []
        file_type = 'sample'
        for sample in sample_levels:
            row = [sample]
            row.extend(sample_levels[sample])
            row.append(file_type)
            data.append(row)

        headers = ['sample']
        for factor in factors:
            headers.append(factor.label)
        headers.append('file_type')
        df = pd.DataFrame(data, columns=headers)

        r_dataframe = pandas2ri.py2ri(df)
        return df, r_dataframe

    def run_stats(self, raw_data_dict, groups_dict, mzmatch_outputs, mzmatch_params, save_fixtures):

        analysis_id = self.analysis.id

        groups = self.metadata.get_groups()
        df, metadata = self.convert_to_dataframe(groups)

        r_factors = robjects.StrVector([f.label for f in groups])
        r_contrasts = pandas2ri.py2ri(self.metadata.contrasts)

        databases = self.r_databases
        dbs = self.r_dbs
        wd = self.working_dir

        pimp_run_stats = robjects.r['Pimp.runStats.save']
        pimp_run_stats(raw_data_dict['positive'], raw_data_dict['negative'], analysis_id,
                       r_factors, metadata, r_contrasts,
                       databases, dbs, mzmatch_outputs, mzmatch_params,
                       save_fixtures, wd)

    def run_pipeline(self):

        xcms_params = self.get_value(self.pimp_params, 'xcms.params')
        mzmatch_params = self.get_value(self.pimp_params, 'mzmatch.params')
        peakml_params = self.get_value(self.pimp_params, 'peakml.params')
        mzmatch_outputs = self.get_value(self.pimp_params, 'mzmatch.outputs')
        mzmatch_filters = self.get_value(self.pimp_params, 'mzmatch.filters')
        n_slaves = multiprocessing.cpu_count()

        # still assuming that there are two polarities: pos and neg
        raw_data_dict = {}
        groups_dict = {}
        for polarity in self.metadata.files:
            logger.info('Processing %s polarity', polarity)
            raw_data, groups = self.process_raw_data(polarity, xcms_params, mzmatch_params,
                                                  peakml_params, mzmatch_outputs, mzmatch_filters, n_slaves)
            raw_data_dict[polarity] = raw_data
            groups_dict[polarity] = groups

        save_fixtures = True
        self.run_stats(raw_data_dict, groups_dict, mzmatch_outputs, mzmatch_params, save_fixtures)

        xml_file_name = ".".join(["_".join(["analysis", str(self.analysis.id)]), "xml"])
        xml_file_path = os.path.join(settings.MEDIA_ROOT, 'projects', str(self.project.id), xml_file_name)

        return xml_file_path

    def create_peakml(self, polarity, polarity_dir,
                      xcms_params, mzmatch_params, peakml_params,
                      mzmatch_outputs, n_slaves):
        ''' Performs peak detection using centwave, rt alignment using xcms (optional) and generate peakml files. '''

        posvector = robjects.StrVector(self.metadata.files['positive'])
        negvector = robjects.StrVector(self.metadata.files['negative'])
        r_files = robjects.ListVector({'positive': posvector, 'negative': negvector})

        files = self.get_value(r_files, polarity)
        xset = self.peak_detection(files, xcms_params, n_slaves)
        rt_correction_method = self.get_value(mzmatch_params, 'rt.alignment')[0]
        xseto = self.rt_correct(xset, rt_correction_method, peakml_params, mzmatch_outputs, n_slaves, True)
        self.generate_peakml_files(xseto, polarity_dir, self.analysis.id, peakml_params)

    def generate_peaksets(self, polarity, polarity_dir, combined_dir, mzmatch_params):
        ''' Separates samples into groups and match peakml files in each group to produce aligned peaksets '''

        combine_info, combined_dir = self.generate_combinations(polarity, combined_dir)
        combination_paths = self.copy_files(polarity_dir, combined_dir, combine_info)

        ppm = self.get_value(mzmatch_params, 'ppm')[0]
        rtwindow = self.get_value(mzmatch_params, 'rtwindow')[0]
        combine_type = self.get_value(mzmatch_params, 'combination')[0]

        self.combine_all(combine_info, combined_dir, combination_paths, ppm, rtwindow, combine_type)

        i = 0
        group_dict = {}
        for i in range(len(combine_info)):
            combi, index, factors, files = combine_info[i]
            if len(files) > 0:
                group_dict[combi] = robjects.StrVector(files)
        r_combi = robjects.ListVector(group_dict)
        return r_combi

    def filter_peaksets(self, combined_dir, mzmatch_params):
        peaksets = self.list_peakml_files_in(combined_dir)
        rsd = self.get_value(mzmatch_params, 'rsd')[0]
        peaksets = self.rsd_filter(peaksets, rsd)
        return peaksets

    def combine_final(self, polarity, peaksets, mzmatch_params, mzmatch_outputs):
        out_file = self.get_value(mzmatch_outputs, 'final.combined.peakml.file')[0]
        out_file = os.path.abspath(out_file)

        ppm = self.get_value(mzmatch_params, 'ppm')[0]
        rtwindow = self.get_value(mzmatch_params, 'rtwindow')[0]
        combine_type = self.get_value(mzmatch_params, 'combination')[0]
        NULL = robjects.r("NULL")
        self.combine_peaksets(peaksets, out_file, NULL, ppm, rtwindow, combine_type)

        return out_file

    def filter_final(self, polarity, in_file, mzmatch_filters, mzmatch_params, mzmatch_outputs):

        noise_filter = robjects.r['Pimp.noiseFilter']
        apply_noise_filter = self.get_value(mzmatch_filters, 'noise')[0]
        if apply_noise_filter:
            noise = self.get_value(mzmatch_params, 'noise')[0]
            out_file = self.get_value(mzmatch_outputs, 'final.combined.noise.filtered.file')[0]
            out_file = os.path.abspath(out_file)
            noise_filter(in_file, out_file, noise)
        else:
            out_file = in_file

        simple_filter = robjects.r['Pimp.simpleFilter']
        in_file = out_file
        filter_ppm = self.get_value(mzmatch_params, 'ppm')[0]
        filter_minintensity = self.get_value(mzmatch_params, 'minintensity')[0]
        filter_mindetections = self.get_value(mzmatch_params, 'mindetections')[0]
        out_file = self.get_value(mzmatch_outputs, 'final.combined.simple.filtered.file')[0]
        out_file = os.path.abspath(out_file)
        simple_filter(in_file, out_file, filter_ppm, filter_minintensity, filter_mindetections)

        return out_file

    def gap_filling(self, polarity, in_file, peakml_params, mzmatch_outputs):

        out_file = self.get_value(mzmatch_outputs, 'final.combined.gapfilled.file')[0]
        out_file = os.path.abspath(out_file)

        ionisation = self.get_value(peakml_params, 'ionisation')[0]
        ppm = self.get_value(peakml_params, 'ppm')[0]
        rtwindow = self.get_value(peakml_params, 'rtwin')[0]
        gap_filler = robjects.r['Pimp.gapFilling']
        gap_filler(in_file, out_file, ionisation, ppm, rtwindow)

        return out_file

    def related_peaks(self, polarity, in_file, mzmatch_params, mzmatch_outputs):

        out_file = self.get_value(mzmatch_outputs, 'final.combined.related.file')[0]
        out_file = os.path.abspath(out_file)

        basepeak_file = self.get_value(mzmatch_outputs, 'final.combined.basepeaks.file')[0]
        basepeak_file = os.path.abspath(basepeak_file)

        ppm = self.get_value(mzmatch_params, 'ppm')[0]
        rtwindow = self.get_value(mzmatch_params, 'rtwindow')[0]
        related_peaks = robjects.r['Pimp.relatedPeaks']
        related_peaks(in_file, out_file, basepeak_file, ppm, rtwindow)

        return out_file, basepeak_file

    def identify(self, polarity, in_file, databases, groups, mzmatch_params, mzmatch_outputs):

        args = {
            'in_file'           : in_file,
            'databases'         : databases,
            'groups'            : groups,
            'mzmatch.outputs'   : mzmatch_outputs,
            'mzmatch.params'    : mzmatch_params,
            'polarity'          : polarity
        }

        pimp_identify = robjects.r['Pimp.identify.metabolites']
        raw_data = pimp_identify(**args)
        return raw_data

    ############################################################
    # peak detection
    ############################################################

    def peak_detection(self, files, xcms_params, n_slaves):

        # collect the parameters
        args = {
            'files'           : files,
            'method'          : self.get_value(xcms_params, 'method'),
            'ppm'             : self.get_value(xcms_params, 'ppm'),
            'peakwidth'       : self.get_value(xcms_params, 'peakwidth'),
            'snthresh'        : self.get_value(xcms_params, 'snthresh'),
            'prefilter'       : self.get_value(xcms_params, 'prefilter'),
            'integrate'       : self.get_value(xcms_params, 'integrate'),
            'mzdiff'          : self.get_value(xcms_params, 'mzdiff'),
            'verbose.columns' : self.get_value(xcms_params, 'verbose.columns'),
            'fitgauss'        : self.get_value(xcms_params, 'fitgauss'),
            'nSlaves'         : n_slaves
        }

        # call centwave
        xcms_set = robjects.r['xcmsSet']
        xset = xcms_set(**args)
        return xset

    def rt_correct(self, xset, method, peakml_params, mzmatch_outputs, n_slaves, verbose):

        if method == 'obiwarp':
            retcor = robjects.r['retcor']
            xset_aln = retcor(xset, method='obiwarp', profStep=0.01)
        elif method == 'loess':
            retcor = robjects.r['retcor']
            xset_aln = retcor(xset, method='loess', family="symmetric")
        else:
            xset_aln = xset

        filepaths = robjects.r['filepaths']
        fp = filepaths(xset_aln)

        split = robjects.r['split']
        xseto = split(xset_aln, fp)
        return xseto

    ############################################################
    # peakml generation
    ############################################################

    def generate_peakml_files(self, xseto, polarity_dir, analysis_id, peakml_params):

        write_peakml = robjects.r['PeakML.xcms.write.SingleInstance']
        ionisation = self.get_value(peakml_params, 'ionisation')
        add_scans = self.get_value(peakml_params, 'addscans')
        write_rejected = self.get_value(peakml_params, 'writeRejected')
        apodisation_filter = self.get_value(peakml_params, 'ApodisationFilter')
        ppm = self.get_value(peakml_params, 'ppm') # this doesn't seem to be set inside peakml_params ..?
        if ppm == 0:
            ppm = 5

        peakml_files = []
        regex = re.compile(re.escape('mzxml'), re.IGNORECASE)

        names = robjects.r['names']
        xset_names = names(xseto)
        for name in xset_names:
            replaced = regex.sub('peakml', name)
            outfile = os.path.join(polarity_dir, os.path.basename(replaced))
            peakml_files.append(outfile)

        for i in range(len(peakml_files)):
            logger.debug('Now creating %s' % peakml_files[i])
            write_peakml(xseto[i], outputfile=peakml_files[i], ionisation=ionisation,
                         addscans=add_scans, writeRejected=write_rejected,
                         ApodisationFilter=apodisation_filter, ppm=ppm)

    ############################################################
    # separate files into groups
    ############################################################

    def generate_combinations(self, polarity, combined_dir):

        factors = self.metadata.get_groups(self.project)
        logger.debug(factors)
        dims = []
        for f in factors:
            logger.debug(f.label)
            for lev in f.levels:
                logger.debug('- %s %s', lev, f.level_files[lev])
            dims.append(len(f.levels))

        mat = np.empty(dims, dtype=object)
        logger.debug(mat.shape)
        parent = Tree(None, 'root', -1, None)
        parent.level_files = set(self.metadata.get_short_names(polarity))
        self.populate_tree(parent, factors)
        output = self.print_tree(parent, mat, [])
        logger.debug(output)

        out_file = os.path.join(combined_dir, 'combined.tsv')
        combine_info = self.write_combinations(factors, mat, out_file)

        return combine_info, combined_dir

    def populate_tree(self, parent, factors):
        depth = parent.depth + 1
        if depth > len(factors)-1:
            return
        factor = factors[depth]
        nodes = []
        for level in factor.levels:
            node = Tree(factor, level, depth, parent)
            self.populate_tree(node, factors)

    def print_tree(self, node, mat, coord):
        if node.level_idx is not None:
            coord.append(node.level_idx)
        output = ''.join(['\t' for i in range(node.depth)])
        output += '%d %s %s : %s at %s\n' % (node.depth, node.factor, node.level_label,
                                             node.level_files, coord)
        mat[tuple(coord)] = node.level_files # coord must be a tuple
        for child in node.children:
            new_coord = list(coord) # copy
            output += self.print_tree(child, mat, new_coord)
        return output

    def write_combinations(self, factors, mat, out_file):

        parent_dir = os.path.dirname(out_file)
        self.create_if_not_exist(parent_dir)

        rows = []
        with open(out_file, 'w') as f:
            i = 0
            for index, files in np.ndenumerate(mat):

                combi = 'group_%s' % i
                row = (combi, index, self.index_to_string(factors, index), list(files))
                rows.append(row)

                s = '%s\t%s\t%s\t%s\n' % row
                f.write(s)
                i += 1
        return rows

    def index_to_string(self, factors, index):
        assert len(factors) == len(index)
        output = []
        for d in range(len(factors)):
            f = factors[d]
            idx = index[d]
            output.append(f.levels[idx])
        return ','.join(output)

    def copy_files(self, polarity_dir, combined_dir, combine_info):

        to_process = []
        for row in combine_info:

            logger.debug(row)
            combi_label, coord, description, files = row

            one_combination = os.path.join(combined_dir, combi_label)
            if not os.path.exists(one_combination):
                os.makedirs(one_combination)

            # copy files
            for f_name in files:
                abs_dir = os.path.abspath(polarity_dir)
                source = os.path.join(abs_dir, f_name + '.peakml')
                target = one_combination
                shutil.copy(source, target)

            to_process.append(one_combination)

        return to_process

    ############################################################
    # matching across groups
    ############################################################

    def combine_all(self, combine_info, combined_dir, combination_paths,
                      combine_ppm, combine_rtwindow, combine_type):

        assert len(combine_info) == len(combination_paths)
        for i in range(len(combine_info)):

            combine_label, coord, description, files = combine_info[i]
            one_combination = combination_paths[i]
            if len(files) > 0:
                logger.info('Processing %s', one_combination)
                self.combine_single_combi(one_combination, combined_dir, combine_label,
                               combine_ppm, combine_rtwindow, combine_type)
            else:
                logger.info('Nothing to combine in %s', one_combination)

    def combine_single_combi(self, one_combination, combined_dir, label,
                            ppm, rtwindow, combine_type):

        one_combination_path = os.path.abspath(one_combination)
        input_list = self.list_peakml_files_in(one_combination_path)
        out_file = os.path.join(combined_dir, label + '.peakml')
        self.combine_peaksets(input_list, out_file, label, ppm, rtwindow, combine_type)

    def combine_peaksets(self, input_list, out_file, label, ppm, rtwindow, combine_type):

        peakml_list_str = ','.join(input_list)
        files = robjects.StrVector([peakml_list_str])
        combine_peakml = robjects.r['Pimp.combineSingle']
        combine_peakml(files, out_file, label, ppm, rtwindow, combine_type)

    ############################################################
    # filters --- can be chained together ??
    ############################################################

    def rsd_filter(self, in_peaksets, rsd):

        rsd_filter_peakml = robjects.r['Pimp.rsdSingle']
        out_peaksets = []
        for in_file in in_peaksets:
            basename, extension = os.path.splitext(in_file)
            out_file = basename + '_rsd' + extension
            rej_file = basename + '_rsdrej' + extension
            rsd_filter_peakml(in_file, out_file, rej_file, rsd)
            out_peaksets.append(out_file)

        return out_peaksets

    ############################################################
    # common functions
    ############################################################

    def list_peakml_files_in(self, input_dir):
        dir_content = os.listdir(input_dir)
        peakml_list = []
        for item in dir_content:
            if item.endswith(".peakml"):
                full_path = os.path.join(input_dir, item)
                peakml_list.append(os.path.abspath(full_path))
        return peakml_list

    def get_value(self, r_vect, key):
        return r_vect[r_vect.names.index(key)]

    def get_env_heap_size(self):
        xmx = getString('PIMP_JAVA_PARAMETERS', '')
        found = re.findall(r'\d+', xmx)
        heapsize = int(found[0])
        return heapsize

    def get_env_packrat_lib_path(self):
        packrat_lib_path = getNeededString('R_LIBS_USER')
        return packrat_lib_path

    def create_if_not_exist(self, directory):
        if not os.path.exists(directory):
            logger.info('Creating %s' % directory)
            os.makedirs(directory)

    def create_input_directories(self, polarity, mzmatch_outputs):
        polarity_dir = self.get_value(mzmatch_outputs, 'polarity.folder')[0]
        polarity_dir = os.path.abspath(polarity_dir)
        combined_dir = os.path.join(polarity_dir, 'combined')
        self.create_if_not_exist(polarity_dir)
        self.create_if_not_exist(combined_dir)
        return polarity_dir, combined_dir

class Rpy2PipelineMetadata(object):

    def __init__(self, analysis, project):

        self.analysis = analysis
        self.project = project
        self.experiment = self.analysis.experiment

        self.files = self.get_files()
        self.groups = self.get_groups()
        self.stds = self.get_standards()
        self.contrasts = self.get_comparisons()
        self.databases = self.get_databases()


    def remove_first_two(self, path):
        tokens = path.split('/')
        new_path = '/'.join(tokens[2:])
        return new_path

    def strip_project_from_path(self, path_list):
        processed = []
        for path in path_list:
            if type(path) is tuple:
                first = self.remove_first_two(path[0])
                second = self.remove_first_two(path[1])
                new_path = (first, second)
            else:
                new_path = self.remove_first_two(path)
            processed.append(new_path)
        return processed

    def get_files(self):
        samples = Sample.objects.filter(attribute__comparison__experiment = self.experiment.id).distinct()
        pos_samples = Picture.objects.filter(posdata__sample__in=samples).values_list('file', flat=True)
        neg_samples = Picture.objects.filter(negdata__sample__in=samples).values_list('file', flat=True)

        file_list = {}
        file_list['positive'] = self.strip_project_from_path(pos_samples)
        file_list['negative'] = self.strip_project_from_path(neg_samples)
        return file_list

    def get_short_names(self, polarity):
        files = self.get_files()[polarity]
        short_names = []
        for f in files:
            base = os.path.basename(f)
            parts = os.path.splitext(base)
            front = parts[0]
            short_names.append(front)
        return short_names

    def get_groups(self, project=None):
        if project is not None:
            groups = Group.objects.filter(attribute__sample__project=project)
        else:
            groups = Group.objects.filter(attribute__comparison__experiment = self.experiment).distinct()
        res = Group.objects.filter(id__in=groups).values_list('name','attribute__name','attribute__sample__name')
        data = [row for row in res]

        headers = ['factor', 'level', 'sample']
        df = pd.DataFrame(data, columns=headers)

        factors = []
        fs = df.factor.unique()
        for f_label in fs:

            # get rid of utf8 encoding
            f_label = f_label.encode('ascii','ignore')

            # create Factor based on the dataframe values
            factor = Factor(f_label)
            factor_df = df.loc[df['factor'] == f_label]
            levels = factor_df.level.unique()

            # get the samples in each level
            for level_label in levels:

                level_label = level_label.encode('ascii','ignore')
                level_df = factor_df.loc[factor_df['level'] == level_label]
                samples = level_df[['sample']].values.flatten().tolist()

                # strip the extension from samples
                processed = []
                for samp in samples:
                    filename, file_extension = os.path.splitext(samp)
                    processed.append(filename)

                factor.add_level(level_label, processed)

            factors.append(factor)

        return factors

    def get_standards(self):
        standards = CalibrationSample.objects.filter(project=self.project, attribute__name='standard').values_list(
            'standardFile__data__file', flat=True)
        standard_list = self.strip_project_from_path(standards)
        return standard_list

    def get_calibration_samples(self, samp_type):
        # type is either 'blank' or 'qc'
        cal = CalibrationSample.objects.filter(project=self.project, attribute__name=samp_type).values_list(
            'standardFile__posdata__file', 'standardFile__negdata__file')
        cal_list = self.strip_project_from_path(cal)
        return cal_list

    def get_comparisons(self):
        comparisons = Comparison.objects.filter(experiment=self.experiment).values_list(
            'id', 'name', 'attribute__id', 'attribute__group__name', 'attribute__name', 'attributecomparison__group')
        data = [list(row) for row in comparisons]
        headers = ['id', 'comparison', 'attribute_id', 'factor', 'level', 'group']
        df = pd.DataFrame(data, columns=headers)
        df['level'] = df['level'].astype(str)
        return df

    def get_databases(self):
        databases = Database.objects.filter(params__analysis=self.analysis).values_list('name', flat=True)
        return list(databases)

class Tree(object):

    def __init__(self, factor, level_label, depth, parent):

        self.parent = parent
        parent_files = set()
        if self.parent is not None:
            self.parent.children.append(self)
            parent_files = self.parent.level_files

        self.depth = depth
        self.factor = factor
        self.children = []
        self.level_label = level_label

        level_files = set()
        if factor is not None:
            level_files = set(factor.level_files[level_label])
            self.level_idx = factor.level_indices[level_label]
        else:
            self.level_idx = None
        self.level_files = level_files.intersection(parent_files)

    def __repr__(self):
        output = ' factor %s (%s) depth=%d children=%d' % (self.factor, self.level_label, self.depth, len(self.children))
        return output

class Factor(object):

    def __init__(self, factor_label):
        self.label = factor_label
        self.levels = [] # ordering is important
        self.level_indices = {}
        self.level_files = {}

    def add_level(self, level_label, level_files):
        self.levels.append(level_label)
        self.level_files[level_label] = level_files
        self.level_indices[level_label] = self.levels.index(level_label)

    def get_level(self, sample):
        for level in self.levels:
            if sample in self.level_files[level]:
                return level
        return np.nan

    def __repr__(self):
        return self.label + ' with ' + str(len(self.levels)) + ' levels'
