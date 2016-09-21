import multiprocessing
import os
import re
import shutil

from django.conf import settings
from rpy2.robjects.packages import importr

import numpy as np
from pimp.settings import getString
import rpy2.robjects as robjects

class Rpy2Pipeline(object):

    # read and think about this:
    # http://stackoverflow.com/questions/5707382/is-multiprocessing-with-rpy-safe            
    def __init__(self, analysis, project, saveFixtures):

        self.analysis = analysis
        self.project = project
        self.saveFixtures = saveFixtures
        self.metadata = Rpy2PipelineMetadata(analysis, project)
        self.connect_to_rpy2()
        
    def connect_to_rpy2(self): 

        print '******************************************'
        print 'Setup rpy2 connection'
        print '******************************************'
        
        packrat_lib_path = self.get_env_packrat_lib_path()
        set_lib_path = robjects.r['.libPaths']
        set_lib_path(packrat_lib_path)

        importr('PiMP')    
        base = importr('base')
        base.options('java.parameters=paste("-Xmx",1024*8,"m",sep=""')

        # I think this should be called only once??
        args = {
            'memorysize' : self.get_env_heap_size(),
            'version.1'  : False
        }
        mzmatch_init = robjects.r['mzmatch.init']
        mzmatch_init(**args)
                        
    def setup(self):
        
        print 'Setup called'
        
        # TODO: we could do this in Python ..
        get_pimp_wd = robjects.r['Pimp.getPimpWd']
        self.working_dir = get_pimp_wd(self.project.id)
    
        # TODO: we could do this in Python ??
        validate_input = robjects.r['Pimp.validateInput']
        validate_input(self.analysis.id, self.metadata.r_files, self.metadata.r_groups, self.working_dir)
    
        # TODO: we could do this in Python !!
        get_analysis_params = robjects.r['Pimp.getAnalysisParams']
        self.pimp_params = get_analysis_params(self.analysis.id)
        
        # create analysis dir
        create_analysis_dir = robjects.r['Pimp.createAnalysisDir']        
        # pimp_params$mzmatch.outputs will be updated inside to point to the right analysis folder
        pimp_params = create_analysis_dir(self.analysis.id, self.pimp_params)
    
        # generate std xml
        generate_std_xml = robjects.r('Pimp.generateStdXml')
        output = generate_std_xml(self.metadata.r_stds, self.metadata.r_databases, pimp_params, self.working_dir)
        self.metadata.r_dbs = output[output.names.index('DBS')]
        self.metadata.r_databases = output[output.names.index('databases')]
                
    ############################################################
    # pipeline methods to process raw data
    ############################################################

    def process_raw_data(self, polarity, xcms_params, mzmatch_params, 
                         peakml_params, mzmatch_outputs, mzmatch_filters, n_slaves):
                                                    
        format_mzmatch_outputs = robjects.r['Pimp.getFormattedMzmatchOutputs']
        formatted_mzmatch_outputs = format_mzmatch_outputs(self.analysis.id, polarity, mzmatch_outputs)
        polarity_dir, combined_dir = self.create_input_directories(polarity, formatted_mzmatch_outputs)

        print '------------------------------------------------'
        print polarity, polarity_dir, combined_dir
        print '------------------------------------------------'

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
        databases = self.metadata.r_dbs
        groups = r_combi
        raw_data = self.identify(polarity, out_file, databases, groups, mzmatch_params, formatted_mzmatch_outputs)        
        return raw_data, r_combi

    def run_stats(self, raw_data_dict, analysis_id, groups_dict, factors, 
                  comparison_names, contrasts, databases, dbs, mzmatch_outputs, saveFixtures, wd):
#         assert groups_dict['positive'] == groups_dict['negative']
        pimp_run_stats = robjects.r['Pimp.runStats.save']        
        pimp_run_stats(raw_data_dict['positive'], raw_data_dict['negative'], analysis_id, 
                       groups_dict['positive'], factors,
                       comparison_names, contrasts, databases, dbs, 
                       mzmatch_outputs, saveFixtures, wd)

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
            raw_data, groups = self.process_raw_data(polarity, xcms_params, mzmatch_params, 
                                                  peakml_params, mzmatch_outputs, mzmatch_filters, n_slaves)
            raw_data_dict[polarity] = raw_data
            groups_dict[polarity] = groups
            
        save_fixtures = True    
        self.run_stats(raw_data_dict, self.analysis.id, groups_dict, self.metadata.r_groups, 
                       self.metadata.r_contrasts, self.metadata.r_names, 
                       self.metadata.r_databases, self.metadata.r_dbs, 
                       mzmatch_outputs, save_fixtures, self.working_dir)
            
        return_code = 0
        xml_file_name = ".".join(["_".join(["analysis", str(self.analysis.id)]), "xml"])
        xml_file_path = os.path.join(settings.MEDIA_ROOT, 'projects', str(self.project.id), xml_file_name)

        return return_code, xml_file_path
            
    def create_peakml(self, polarity, polarity_dir, 
                      xcms_params, mzmatch_params, peakml_params, 
                      mzmatch_outputs, n_slaves):
        ''' Performs peak detection using centwave, rt alignment using xcms (optional) and generate peakml files. '''
                    
        files = self.get_value(self.metadata.r_files, polarity)
        xset = self.peak_detection(files, xcms_params, n_slaves) 
        rt_correction_method = self.get_value(mzmatch_params, 'rt.alignment')[0]            
        fp, xseto = self.rt_correct(xset, rt_correction_method, peakml_params, mzmatch_outputs, n_slaves, True)   
        self.generate_peakml_files(xseto, fp, polarity_dir, self.analysis.id, peakml_params)  

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
        return fp, xseto   

    ############################################################
    # peakml generation
    ############################################################             
    
    def generate_peakml_files(self, xseto, fp, polarity_dir, analysis_id, peakml_params):
        
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
        for single_fp in fp:
            replaced = regex.sub('peakml', single_fp)
            outfile = os.path.join(polarity_dir, os.path.basename(replaced))
            peakml_files.append(outfile)            
        
        for i in range(len(peakml_files)):
            print 'Now creating %s' % peakml_files[i]
            write_peakml(xseto[i], outputfile=peakml_files[i], ionisation=ionisation, 
                         addscans=add_scans, writeRejected=write_rejected, 
                         ApodisationFilter=apodisation_filter, ppm=ppm)    

    ############################################################
    # separate files into groups
    ############################################################  
    
    def generate_combinations(self, polarity, combined_dir):
                                
        factors = self.metadata.get_groups()        
        print factors
        dims = []
        for f in factors:
            print f.label
            for lev in f.levels:
                print ' -', lev, f.level_files[lev]
            dims.append(len(f.levels))             

        mat = np.empty(dims, dtype=object)
        print mat.shape
        parent = Tree(None, 'root', -1, None)
        parent.level_files = set(self.metadata.get_short_names(polarity))
        self.populate_tree(parent, factors)
        output = self.print_tree(parent, mat, [])
        # print output
        
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
    
            print row
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
                print 'Processing', one_combination
                self.combine_single_combi(one_combination, combined_dir, combine_label, 
                               combine_ppm, combine_rtwindow, combine_type)                                    
            else:
                print 'Nothing to combine in', one_combination
         
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
        packrat_lib_path = getString('R_LIBS_USER', '')
        return packrat_lib_path
        
    def create_if_not_exist(self, directory):
        if not os.path.exists(directory):
            print 'Creating %s' % directory
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

        self.files = self.get_files()
        self.groups = self.get_groups()
        self.stds = self.get_standards()
        self.contrasts, self.names = self.get_comparisons()
        self.databases = self.get_databases()
        
        ##############################################
        # convert from python into R data structures    
        ##############################################

        # files
        posvector = robjects.StrVector(self.files['positive'])
        negvector = robjects.StrVector(self.files['negative'])
        self.r_files = robjects.ListVector({'positive': posvector, 'negative': negvector})        
        
        # groups
        outer_dict = {}
        for factor in self.groups:
            group_dict = {}
            for level in factor.levels:
                group_dict[level] = robjects.StrVector(factor.level_files[level])
            item = robjects.ListVector(group_dict)
            outer_dict[factor.label] = item    
        self.r_groups = robjects.ListVector(outer_dict)

        # stds
        self.r_stds = robjects.StrVector(self.stds)        

        # contrasts
        self.r_contrasts = robjects.StrVector(self.contrasts)
        self.r_names = robjects.StrVector(self.names)        

        # databases
        self.r_databases = robjects.StrVector(self.databases)  
        self.r_dbs = robjects.StrVector([])

    def get_files(self):
        file_list = {}
        file_list['positive'] = [
            'samples/POS/Beer_4_full1.mzXML', 'samples/POS/Beer_4_full2.mzXML', 'samples/POS/Beer_4_full3.mzXML',
            'samples/POS/Beer_1_full1.mzXML', 'samples/POS/Beer_1_full2.mzXML', 'samples/POS/Beer_1_full3.mzXML',
            'samples/POS/Beer_2_full1.mzXML', 'samples/POS/Beer_2_full2.mzXML', 'samples/POS/Beer_2_full3.mzXML',
            'samples/POS/Beer_3_full1.mzXML', 'samples/POS/Beer_3_full2.mzXML', 'samples/POS/Beer_3_full3.mzXML'
        ]
        file_list['negative'] = [
            'samples/NEG/Beer_4_full1.mzXML', 'samples/NEG/Beer_4_full2.mzXML', 'samples/NEG/Beer_4_full3.mzXML',
            'samples/NEG/Beer_1_full1.mzXML', 'samples/NEG/Beer_1_full2.mzXML', 'samples/NEG/Beer_1_full3.mzXML',
            'samples/NEG/Beer_2_full1.mzXML', 'samples/NEG/Beer_2_full2.mzXML', 'samples/NEG/Beer_2_full3.mzXML',
            'samples/NEG/Beer_3_full1.mzXML', 'samples/NEG/Beer_3_full2.mzXML', 'samples/NEG/Beer_3_full3.mzXML'
        ]
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
        
    def get_groups(self):

        factors = []

        f1 = Factor('beer_smell')
        f1.add_level('smell_good', ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3',
                                    'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3',
                                    'Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3'])
        f1.add_level('smell_bad', ['Beer_4_full1', 'Beer_4_full2', 'Beer_4_full3'])
        factors.append(f1)

        f2 = Factor('beer_colour')
        f2.add_level('colour_dark', ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3', 
                              'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'])
        f2.add_level('colour_light', ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3', 
                               'Beer_4_full1', 'Beer_4_full2', 'Beer_4_full3'])
        factors.append(f2)

        f1 = Factor('beer_taste')
        f1.add_level('taste_delicious', ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3', 
                                   'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'])
        f1.add_level('taste_okay', ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3'])
        f1.add_level('taste_awful', ['Beer_4_full1', 'Beer_4_full2', 'Beer_4_full3'])
        factors.append(f1)
        
        return factors
        
    def get_standards(self):
        standard_list = [
            'calibration_samples/standard/Std1_1_20150422_150810.csv',
            'calibration_samples/standard/Std2_1_20150422_150711.csv',
            'calibration_samples/standard/Std3_1_20150422_150553.csv'
        ]
        return standard_list
    
    # need to think about what data structure to store the comparisons ...
    def get_comparisons(self):
        comparisons = ['beer1', 'beer4']
        comparison_names = ['beer_comparison']
        return comparisons, comparison_names
    
    def get_databases(self):
        database_list = ['kegg', 'hmdb', 'lipidmaps', 'standard']
        return database_list
        
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
        self.levels = []
        self.level_indices = {}
        self.level_files = {}
        
    def add_level(self, level_label, level_files):
        self.levels.append(level_label)
        self.level_files[level_label] = level_files
        self.level_indices[level_label] = self.levels.index(level_label)
        
    def __repr__(self):
        return self.label + ' with ' + str(len(self.levels)) + ' levels'
