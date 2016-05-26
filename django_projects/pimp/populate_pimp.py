#!/usr/bin/env python
import os
import csv
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings')

import django
django.setup()

import jsonpickle
from experiments.models import DefaultParameter, Database
from frank.models import AnnotationTool, ExperimentalProtocol, AnnotationToolProtocol
from compound.models import Pathway, SuperPathway, DataSource, DataSourceSuperPathway

def populate():
    iqr_parameter = add_default_parameter(
        name = "iqr",
        value = 0.5,
        state = True,
    )

    rsd_parameter = add_default_parameter(
        name = "rsd",
        value = 0.5,
        state = True,
    )

    noise_parameter = add_default_parameter(
        name = "noise",
        value = 0.8,
        state = True,
    )

    ppm_parameter = add_default_parameter(
        name = "ppm",
        value = 3,
        state = True,
    )

    min_detection = add_default_parameter(
        name = "mindetections",
        value = 3,
        state = True,
    )

    min_intensity = add_default_parameter(
        name = "minintensity",
        value = 5000,
        state = True,
    )

    rt_window = add_default_parameter(
        name = "rtwindow",
        value = 0.05,
        state = True,
    )

    rt_alignment = add_default_parameter(
        name = "rt.alignment",
        value = None,
        state = True,
    )

    # normalization = add_default_parameter(
    #     name = "normalization",
    #     value = None,
    #     state = False,
    # )

    kegg_db = add_database(
        name = "kegg"
    )

    hmdb_db = add_database(
        name = "hmdb"
    )

    lipidmaps_db = add_database(
        name = "lipidmaps"
    )

    standard_db = add_database(
        name = "standard"
    )

    mass_bank_annotation_tool = add_annotation_tool(
        name = 'MassBank',
        default_params= {
            'client': 'http://www.massbank.jp/api/services/MassBankAPI?wsdl',
            'type': '1',
        }
    )

    NIST_annotation_tool = add_annotation_tool(
        name = 'NIST',
        default_params={
            'source': 'C:\\2013_06_04_MSPepSearch_x32\\MSPepSearch.exe',
            'library_path': 'C:\\NIST14\\MSSEARCH',
        }
    )
    
    SIRIUS_annotation_tool = add_annotation_tool(
        name = 'SIRIUS',
        default_params = {},
    )    

    network_sampler_annotation_tool = add_annotation_tool(
        name = 'Network Sampler',
        default_params = {},
    )

    # this needs to be filled in properly
    precursor_mass_filter_annotation_tool = add_annotation_tool(
        name = 'Precursor Mass Filter',
        default_params = {},
    )

    clean_annotation_tool = add_annotation_tool(
        name = 'Clean Annotations',
        default_params = {},
    )

    lcms_dda_experimental_protocol = add_experimental_protocol(
        name='Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'
    )

    gcms_dia_experimental_protocol = add_experimental_protocol(
        name='Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation'
    )

    # lcms_dia_experimental_protocol = add_experimental_protocol(
    #     name = 'Liquid-Chromatography Data-Independent Acquisition'
    # )

    mass_bank_protocols = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol,gcms_dia_experimental_protocol],
        mass_bank_annotation_tool
    )

    NIST_protocols = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol,gcms_dia_experimental_protocol],
        NIST_annotation_tool
    )
    
    SIRIUS_protocols = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol],
        SIRIUS_annotation_tool
    )    

    network_sampler_annotation_tool = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol,gcms_dia_experimental_protocol],
        network_sampler_annotation_tool
    )

    # this needs to be filled in properly
    mass_filter_protocols = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol],precursor_mass_filter_annotation_tool
    )

    clean_filter_protocols = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol,gcms_dia_experimental_protocol],
        clean_annotation_tool
    )

    # Pathway population for Kegg
    kegg_datasource = add_datasource(
        name = "kegg"
    )
    header_row = True
    with open('./django_projects/pimp/kegg_pathway_superPathway.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            if header_row:
                header_row = False
            else:
                pathway = add_pathway(
                    name = row[1],
                )
                if row[3] != "NA":
                    superpathway = add_superpathway(
                        name = row[3],
                    )
                else:
                    superpathway = None
                datasource_super_pathway = add_datasource_super_pathway(
                    superpathway = superpathway,
                    pathway = pathway,
                    datasource = kegg_datasource,
                    compound_number = int(row[2]),
                    identifier = row[0],
                )

def add_datasource(name):
    datasource = DataSource.objects.get_or_create(
        name = name,
    )[0]
    print 'Creating datasource - '+name+'...'
    datasource.save()
    return datasource

def add_superpathway(name):
    superpathway = SuperPathway.objects.get_or_create(
        name = name,
    )[0]
    print 'Creating super pathway - '+name+'...'
    superpathway.save()
    return superpathway

def add_pathway(name):
    pathway = Pathway.objects.get_or_create(
        name = name,
    )[0]
    print 'Creating pathway - '+name+'...'
    pathway.save()
    return pathway

def add_datasource_super_pathway(superpathway, pathway, datasource, compound_number, identifier):
    datasource_super_pathway = DataSourceSuperPathway.objects.get_or_create(
        super_pathway = superpathway,
        pathway = pathway,
        data_source = datasource,
        compound_number = compound_number,
        identifier = identifier,
    )[0]
    print 'Creating datasource super pathway - '+datasource.name+' - '+identifier+'...'
    datasource_super_pathway.save()
    return datasource_super_pathway

def add_default_parameter(name, value, state):
    parameter = DefaultParameter.objects.get_or_create(
        name = name,
        value = value,
        state = state,
    )[0]
    print 'Creating default parameter - '+name+'...'
    parameter.save()
    return parameter

def add_database(name):
    database = Database.objects.get_or_create(
       name = name,
    )[0]
    print 'Creating default database - '+name+'...'
    database.save()
    return database

def add_annotation_tool(name, default_params):
    default_params = jsonpickle.encode(default_params)
    annotation_tool = AnnotationTool.objects.get_or_create(
        name = name,
        default_params = default_params,
    )[0]
    print 'Creating default annotation tool - '+name+'...'
    annotation_tool.save()
    return annotation_tool

def add_experimental_protocol(name):
    experimental_protocol = ExperimentalProtocol.objects.get_or_create(
       name = name,
    )[0]
    print 'Creating experimental protocol - '+name+'...'
    experimental_protocol.save()
    return experimental_protocol

def add_annotation_tool_protocols(protocols_list, annotation_tool):
    for protocol in protocols_list:
        print 'Adding '+protocol.name+' to Annotation Tool '+annotation_tool.name
        annotation_tool_protocol = AnnotationToolProtocol.objects.get_or_create(
            annotation_tool = annotation_tool,
            experimental_protocol = protocol
        )

# Execution starts here
if __name__=='__main__':
    print "Populating default parameters..."
    populate()
