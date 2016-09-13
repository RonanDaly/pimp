import os

from django.conf import settings
from rpy2.robjects.packages import importr

import rpy2.robjects as robjects

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
        self.level_files = level_files.intersection(parent_files)
                
    def __repr__(self):
        output = ' factor %s (%s) depth=%d children=%d' % (self.factor, self.level_label, self.depth, len(self.children))
        return output

class Factor(object):
    def __init__(self, factor_label):
        self.label = factor_label
        self.levels = []
        self.level_files = {}
        
    def add_level(self, level_label, level_files):
        self.levels.append(level_label)
        self.level_files[level_label] = level_files
        
    def __repr__(self):
        return self.label + ' with ' + str(len(self.levels)) + ' levels'

class Rpy2PipelineMetadata(object):
    def __init__(self, files, groups, stds, names, contrasts, databases):
        
        self.files = files
        self.groups = groups
        self.stds = stds
        self.names = names
        self.contrasts = contrasts
        self.databases = databases
        
        ##############################################
        # convert from python into R data structures    
        ##############################################

        # files
        posvector = robjects.StrVector(self.files['positive'])
        negvector = robjects.StrVector(self.files['negative'])
        self.r_files = robjects.ListVector({'positive': posvector, 'negative': negvector})        
        
        # groups
        outer_dict = {}
        for factor in groups:
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
        

class Rpy2Pipeline(object):

    # read and think about this:
    # http://stackoverflow.com/questions/5707382/is-multiprocessing-with-rpy-safe            
    def __init__(self, analysis, project, saveFixtures):

        self.analysis = analysis
        self.project = project
        self.saveFixtures = saveFixtures
        self.metadata = self.get_pipeline_metadata()

        print '******************************************'
        print 'Setup rpy2 connection'
        print '******************************************'
        
        packrat_lib_path = '/Users/joewandy/git/pimp/packrat/lib/x86_64-apple-darwin15.5.0/3.3.1/'
        set_lib_path = robjects.r['.libPaths']
        set_lib_path(packrat_lib_path)

        importr('PiMP')    
        base = importr('base')
        base.options('java.parameters=paste("-Xmx",1024*8,"m",sep=""')
        
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

        f1 = Factor('beer_sample')
        f1.add_level('beer1', ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3'])
        f1.add_level('beer2', ['Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'])
        f1.add_level('beer3', ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3'])
        f1.add_level('beer4', ['Beer_4_full1', 'Beer_4_full2', 'Beer_4_full3'])
        factors.append(f1)

        f2 = Factor('beer_colour')
        f2.add_level('dark', ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3', 
                              'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'])
        f2.add_level('light', ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3', 
                               'Beer_4_full1', 'Beer_4_full2', 'Beer_4_full3'])
        factors.append(f2)

        f1 = Factor('beer_taste')
        f1.add_level('delicious', ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3', 
                                   'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'])
        f1.add_level('okay', ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3'])
        f1.add_level('awful', ['Beer_4_full1', 'Beer_4_full2', 'Beer_4_full3'])
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
        
    def get_pipeline_metadata(self):
        
        files = self.get_files()
        groups = self.get_groups()
        stds = self.get_standards()
        contrasts, names = self.get_comparisons()
        databases = self.get_databases()
        
        metadata = Rpy2PipelineMetadata(files, groups, stds, names, contrasts, databases)        
        return metadata    
    
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
        self.dbs = generate_std_xml(self.metadata.r_stds, self.metadata.r_databases, pimp_params, self.working_dir)
    
        # dump the input parameters out for R debugging
        if self.saveFixtures:
            dump_parameters = robjects.r['Pimp.dumpParameters']
            dump_parameters(self.metadata.r_files, self.metadata.r_groups, self.metadata.r_stds, 
                       self.metadata.r_names, self.metadata.r_contrasts, self.metadata.r_databases, 
                       self.analysis.id, self.project.id, self.working_dir, 
                       pimp_params, self.dbs)        
    
    def run(self):
                                                
        # call the pipeline
        run_pipeline = robjects.r['Pimp.runPipeline']
    #     run_Pipeline(metadata.files, metadata.groups, metadata.stds, 
    #                 metadata.names, metadata.contrasts, metadata.databases, 
    #                 saveFixtures, analysis.id, project.id, working_dir,
    #                 pimp_params, DBS)

        # still assuming that there are two polarities: pos and neg
        for polarity in self.files:
            print polarity
        
        return_code = 0
        xml_file_name = ".".join(["_".join(["analysis", str(self.analysis.id)]), "xml"])
        xml_file_path = os.path.join(settings.MEDIA_ROOT, 'projects', str(self.project.id), xml_file_name)

        return return_code, xml_file_path