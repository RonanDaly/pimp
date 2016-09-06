import os

from django.conf import settings
from rpy2.robjects.packages import importr

import rpy2.robjects as robjects


class Rpy2PipelineMetadata(object):
    def __init__(self, files, groups, stds, names, contrasts, databases):
        self.files = files
        self.groups = groups
        self.stds = stds
        self.names = names
        self.contrasts = contrasts
        self.databases = databases

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
        posvector = robjects.StrVector(file_list['positive'])
        negvector = robjects.StrVector(file_list['negative'])
        files = robjects.ListVector({'positive': posvector, 'negative': negvector})        
        return files
        
    def get_groups(self):
        groups = {
            'beer_taste' : {
                'delicious' : ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3', 'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'],
                'not_bad'   : ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3'],
                'bad'       : ['Beer_4_full1'],
                'awful'     : ['Beer_4_full2', 'Beer_4_full3']
            },
            'beer_colour' : {
                'dark'      : ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3', 'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'],
                'light'     : ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3', 'Beer_4_full1', 'Beer_4_full2', 'Beer_4_full3']
            }
        }
        
        # convert groups from python into rpy2 objects
        outer_dict = {}
        for key in groups.keys():
            inner_dict = groups[key]
            group_dict = {}
            for k in inner_dict.keys():
                group_dict[k] = robjects.StrVector(inner_dict[k])
            item = robjects.ListVector(group_dict)
            outer_dict[key] = item
    
        r_thing = robjects.ListVector(outer_dict)
        return r_thing    
    
    def get_standards(self):
        standard_list = [
            'calibration_samples/standard/Std1_1_20150422_150810.csv',
            'calibration_samples/standard/Std2_1_20150422_150711.csv',
            'calibration_samples/standard/Std3_1_20150422_150553.csv'
        ]
        stds = robjects.StrVector(standard_list)        
        return stds
    
    # need to think about what data structure to store the comparisons ...
    def get_comparisons(self):
        comparisons = ['beer1', 'beer4']
        comparison_names = ['beer_comparison']
        contrasts = robjects.StrVector(comparisons)
        names = robjects.StrVector(comparison_names)        
        return contrasts, names
    
    def get_databases(self):
        database_list = ['kegg', 'hmdb', 'lipidmaps', 'standard']
        databases = robjects.StrVector(database_list)
        return databases
        
    def get_pipeline_metadata(self):
        
        files = self.get_files()
        groups = self.get_groups()
        stds = self.get_standards()
        contrasts, names = self.get_comparisons()
        databases = self.get_databases()
        
        metadata = Rpy2PipelineMetadata(files, groups, stds, names, contrasts, databases)        
        return metadata    
    
    def setup(self):
        
        # TODO: we could do this in Python ..
        get_pimp_wd = robjects.r['Pimp.getPimpWd']
        self.working_dir = get_pimp_wd(self.project.id)
    
        # TODO: we could do this in Python ??
        validate_input = robjects.r['Pimp.validateInput']
        validate_input(self.analysis.id, self.metadata.files, self.metadata.groups, self.working_dir)
    
        # TODO: we could do this in Python !!
        get_analysis_params = robjects.r['Pimp.getAnalysisParams']
        self.pimp_params = get_analysis_params(self.analysis.id)
        
        # create analysis dir
        create_analysis_dir = robjects.r['Pimp.createAnalysisDir']        
        # pimp_params$mzmatch.outputs will be updated inside to point to the right analysis folder
        pimp_params = create_analysis_dir(self.analysis.id, self.pimp_params)
    
        # generate std xml
        generate_std_xml = robjects.r('Pimp.generateStdXml')
        self.dbs = generate_std_xml(self.metadata.stds, self.metadata.databases, pimp_params, self.working_dir)
    
        # dump the input parameters out for R debugging
        if self.saveFixtures:
            dump_parameters = robjects.r['Pimp.dumpParameters']
            dump_parameters(self.metadata.files, self.metadata.groups, self.metadata.stds, 
                       self.metadata.names, self.metadata.contrasts, self.metadata.databases, 
                       self.analysis.id, self.project.id, self.working_dir, 
                       pimp_params, self.dbs)        
    
    def run(self):
                                                
        # call the pipeline
        run_pipeline = robjects.r['Pimp.runPipeline']
    #     run_Pipeline(metadata.files, metadata.groups, metadata.stds, 
    #                 metadata.names, metadata.contrasts, metadata.databases, 
    #                 saveFixtures, analysis.id, project.id, working_dir,
    #                 pimp_params, DBS)
        
        return_code = 0
        xml_file_name = ".".join(["_".join(["analysis", str(self.analysis.id)]), "xml"])
        xml_file_path = os.path.join(settings.MEDIA_ROOT, 'projects', str(self.project.id), xml_file_name)

        return return_code, xml_file_path