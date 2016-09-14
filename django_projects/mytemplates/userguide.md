{% load staticfiles %}

# Getting started

**Please Note**

*For space and portability reasons, PiMP relies on centroided single polarity data in the MzXML format. If you are unable to convert your data into MzXML, please look at this guide (click here).*

## Logging in to PiMP:

To log in to PiMP, go to: [PiMP Homepage](http:/polyomics.mvls.gla.ac.uk/accounts/login/, "PiMP")

Once there, please input your username and password.
If you have not been provided with a username and password, please contact the PiMP administrator. Once you hit enter, or click 'Submit', you should find yourself in the project management page. From here you can see some general information about your projects, collaborators and the amount of storage you have used.

![Project Management Page][project_management]

From here, you can click on 'My Projects' to create a new project and start your analysis.

![My Projects Page][my_projects]

Prerequisites
-------------

To analyse your data, you first need:
1. Your data in MzXML format
2. Three retention time standards files in the appropriate format (click here for downloadable examples ([Standards 1]({% static "userguide/stds1.csv" %}), [Standards 2]({% static "userguide/stds2.csv" %}), [Standards 3]({% static "userguide/stds3.csv" %}))).
3. Your experimental design

Once you have these things available, please click on ‘Create Project’.

![Create Project][create_project]

## Create Project:

To create your project, first give it a title, then a description. The description is useful as it allows you to tag your projects so they are easily browsable. Then click 'Create project'.

![Project Dialog][project_dialog]

## Project Administration:

In ‘Project Administration’, you can add users to your project (via the ‘add users’ button), edit the title of your project or change the description (via the ‘edit title’ and ‘edit’ buttons respectively.

![Project Administration][project_administration]

  Once you have performed any desired administration in this page, enter calibration samples by clicking on the ‘Calibration Samples’ tab.

## Calibration Samples:

To successfully enter a metabolomics experiment, you must first provide a group of supporting data files. These consist of blanks, standards files and pooled/QC files. The blanks and pooled/QCs must be in MzXML format and the standards files must be in CSV format using the default Polyomics standards mixes. MzXML files must be uploaded in pairs: both a positive ionization mode and negative ionization mode version of each file. The pair of files must have the same name. Once a pair is uploaded, this is denoted by + - symbols next to the filename.

![Calibration Samples][calibration_samples]

To upload any of the files, click on the blue button with an up arrow in the Available Samples box. A new window will appear allowing you to drag and drop your files for upload.

## Upload File (calibration data):

Simply drag and drop the blanks and pooled/QC MzXML files and standards files in csv format into the box below, then click the green ‘start upload’ button.

![Upload Files Dialog][upload_files]

MzXML files must be uploaded in pairs: both a positive ionization mode and negative ionization mode version of each file. The pair of files must have the same name. Once a pair is uploaded, this is denoted by + - symbols next to the filename.

Once your samples are uploaded, assign them to their appropriate categories (either standards, blank or QC).

![Assign Calibration Samples][assign_calibration_samples]

To assign your samples to groups, highlight the samples in that group and then click the '+' symbol next to the appropriate group title.

![Assign to QC Group][assign_qc]

You can use the 'search' box to free text filter the file list.

![Search Calibrations][search_calib]

Once all of the files have been uploaded and assigned, click the ‘Sample Management’ tab.

## Sample Management:

To begin uploading files, click the blue ‘upload files’ button in the ‘Samples’ box.  Once your samples are uploaded, you can apply an experimental design by clicking on the ‘Create’ button.

## Experimental Design:

Currently, PiMP supports experiments defined by discrete categories. Thus experiments must be defined in terms of conditions: wild type, mutant, time 0, time 30, no drug, low dose, high dose, etc. You can have as many conditions as you like, although bear in mind that a large number of conditions in a single experiment are hard to visualize effectively – you might be better to create multiple experiments. Once you have defined your conditions, click ‘Next’.

![Experiment Definition][experiment_definition]

## Assign Samples:

You can now drag and drop the files into the conditions you have specified. Once you have completed your assignment, click ‘Submit’, and click on the ‘Analysis’ tab.

## Analysis:
Once you have defined a project and set up the calibration and experimental samples, you can create a new analysis to be submitted to the server, you must click on the ‘+ Create’ button.

![Analysis List][analysis_list]

You may provide an experiment name, and define the comparisons to be made. A comparison is simply a statistical comparison between two experimental groups, e.g. wild type vs mutant, or time 90 vs time 0. You can create as many comparisons as you like: click ‘Add Comparison’ to add another to the list for this experiment. When you have created the comparisons that you are interested in, click ‘Save'.

![Analysis Definition][analysis_definition]

 You are returned to the ‘Analysis’ tab. Your newly created analysis will be at the bottom of the list of current analyses. Simply click ‘Submit analysis’ to submit the analysis to the server. A lot of computational analysis is now performed on the data – please refer to this paper for a description of the analytical process. When the analysis is finished, you can click on the ‘access result’ button, which will bring you to the data exploration environment.



## Upload File (samples):
Simply drag and drop the sample MzXML files into the box below, then click the green ‘start upload’ button. MzXML files must be uploaded in pairs: both a positive ionization mode and negative ionization mode version of each file. The pair of files must have the same name. Once a pair is uploaded, this is denoted by + - symbols next to the filename.

# Results

Once your analysis is completed, it will appear in your 'My Projects' page with a green 'Finished' label in your project card.

![Project Card][project_card]

Click on 'Access Result' to load the data into your browser. A loading screen will appear (please be patient, many projects are quite large!).

![Loading Screen][loading_screen]

## Data Environment:

The first page that loads once you select a completed analysis is the Summary Report.

The PiMP Summary Report displays a summary of the key information from the study. ‘Study’ describes the experimental design that has been chosen, the table shows the groups and number of replicates for each group.

![Summary Page][summary_page]

### Data Processing

Data Processing describes the algorithms applied to the data, with references.

### Quality control

Quality control provides a number of standard methods for assessing the quality of the data: a principal component analysis and the total ion chromatograms for the datasets.

#### Principal Component Analysis

PCA, or principal component analysis is a multivariate statistical method for visualizing large datasets. A good experiment is usually characterized by clear separation between groups. The graph is interactive, and datapoints may be hidden or zoomed in on.

![PCA][pca]

#### Total Ion Chromatograms

Total ion chromatograms give an overview of the total detected masses from the instrument. In a good experiment, samples should overlay to a large extent in the same group, as in the example below. Often a large broad peak is visible towards the end of the chromatogram: this is usually a consequence of salty samples using HILIC chromatography.

![TIC][tic]

# Results

## Summary Page

Results provides a summary of the key findings from the data for each comparison selected by the user. Data from identified (matched by retention time and mass to a standard) compounds are shown separately from annotated (assigned putatively on the basis of mass) compounds. Only significantly changing compounds are listed here for each group.

![Result Histgrams][results]

### Volcano Plots

Next, a volcano plot graphs fold change vs significance, such that the most significant and highest magnitude changes are in the top left and right of the graph. This graph is also interactive and the points can be clicked on to obtain more information about each peak.

![Volcano Plot][volcano]

## Metabolites Tab

Most researchers in metabolomics are more interested in metabolites than peaks, per se. For this reason, we decided to provide any metabolite that evidence existed for in the data. The metabolites tab summarises all the information about detected compounds, allowing the researcher to explore metabolites, pathways and their levels in different sample sets.

![Metabolites Tab][metabolites]

There is a free text search in the top bar that allows the researcher to narrow down on a particular compound or pathway. One can also sort on any of the columns by clicking on the title bar. Additionally, there are drop-down menus to filter the detected metabolites by pathway or superpathway.

Each experimental comparison is listed in the table next to the name and formula of each metabolite. Levels of the metabolite relative to the control condition are shown as log2 fold changes and colour coded red for upregulated and blue for downregulated. Finally, each metabolite is listed as 'annotated' or 'identified' based on the Metabolite Standards Initiative guidelines.

The 'Evidence' panel on the right of the table, activated by selecting a metabolite, provides all the evidence available for that compound, including the reference database the metabolite was found in (including the standards databases uploaded as part of the calibration samples), the structure of the compound, and any peak data associated with the compound. Simply click on the 'chromatogram' button to see an interactive plot of the data.

![Metabolite Peak][metabolite_peak]

Additionally, interactive histograms of the peak can be checked below, by clicking the 'intensities' button.

![Metabolite intensities][metabolite_int]

**An important thing to bear in mind is the relationship of LC-MS peak to metabolite.**

A single peak often can be matched to a single empirical formula, but each formula can be arranged as several structures, which are indistiguishable by mass alone. For this reason, the same peak may be assigned to multiple metabolites, all of which are displayed in the metabolites table. We have done this to avoid making any erroneous assumptions as to the priority of a metabolite assignment. For those metabolites that match by both retention time and mass, they are listed as 'identified' as that metabolite.

Each metabolite can also match several peaks, as several different structures with the same empirical formula may elute during the chromatographic separation (i.e. they will have different retention times), or may occur in multiple polarities (i.e. both positive and negative). For this reason, each 'evidence tab' may have more than one peak associated with it.

*Again, for compounds matched by retention time and mass to a standard, this will be assigned to Peak 1. **IS THIS RIGHT??** *

## Metabolic Maps Tab

The metabolic maps tab contains information about the pathways and that metabolites are assigned to. The information in this tab is derived from the Kyoto Encyclopedia of Genes and Genomes database.

![Metabolic Maps][maps]

Maps are listed along with the total number of compounds in each map, the detected compounds that are listed as either annotated or identified (matched to a mass for the former, or matched to both mass and retention time for the latter), along with a coverage score that describes how much of the pathway has been detected overall.

The list of maps is searchable using the real time search bar at the top of the page.

Clicking on any of the map entries invokes a sidebar containing more information about that map, including the 'Kegg Map button'.

![Metabolic Maps Button][maps_button]

When clicked, the kegg map button will create a new window containing the Kegg map for that particular pathway, along with colour coding of the  metabolites: empty circles are undetected metabolites, gold circles are identified (RT and mass matched) and grey circles are annotated metabolites.

![Kegg Map][kegg_map]

To display a quantitative overview for a specific comparison, click on the 'Map Comparison' combo box in the top left hand corner.

![Select Comparison][maps_select_comp]

This will display the same map with rings around the individual metabolites, colour-coded according to the comparison of their levels, with red being upregulated and blue being downregulated.

![Map Comparison][maps_comparison]

This allows a rapid overview of the data in the context of pathways, and it may be possible to identifiy metabolic chokepoints or enzymatic inhibition, if metabolites upstream an enzyme are upregulated and those downstream of the same enzyme are downregulated.

## Comparisons Tab

The metabolites tab contains every metabolite for which there is evidence of its existence in the dataset. However, there are many compounds detected in a typical metabolomics analysis (especially in LC-MS) for which no known metabolite can be matched.

The majority of these are likely to be contaminants from plasticware, the atmosphere, sample handling, or (in the case of clinical samples) xenobiotics.

In some cases, however, interesting molecules are detected that may be previously undescribed. It may be worth taking a particular unknown compound forward for further characterisation, although this is very challenging and the resources required to fully characterise an unknown compound can be very significant.

For this reason, the comparison tab provides an overview of all differentially regulated compounds.

![Comparison Tab][comparison]

Detected compounds are listed by Peak ID (an arbitrary identifier generated by the software), and can be sorted on any of the columns, *e.g.* based on fold change of a particular comparison.

The sidebar provides detailed information about the peak of interest, including the levels of the compound in the same way as the metabolite tab. Additionally, any annotation determined for the peak is listed at the bottom of the sidebar.

![Comparison Sidebar][comparison_sidebar]

## Peaks Tab

The peaks tab provide an overview of the 'raw data'. Detected features (following processing and filtering) in the LC-MS data are displayed here.

![Peaks Tab][peaks]

Similar to the other tabs, the panel is split into a main window and a sidebar providing detailed information about a specific peak. In the main window, the peak ID, mass and retention time are listed, along with the intensities of each peak in each sample, arranged in groups according to the comparison factors selected in the experimental definition.

The sidebar contains basic information about the peak, the intensities in each sample as an interactive histogram, and the peak chromatogram.

## More tabs

The more tab provides a drop down menu of each comparison. This provides the statistical data for a specific comparison, as well as the typical sidebar providing detailed information about each peak.

![More Tab][more_comparison]

You can sort and filter by log fold change, raw p-value, Benjemini and Hochberg corrected p-value and log odds by using the two text boxes at the top of each column (left being the minimum filter and right being the maximum filter).

![Filters][more_comparison_filters]


It's also possible to search for any peak containing a specific number by using the Peak ID search box at the top of the Peak ID column.

![ID Filters][more_comparison_id_filters]

## Finally

We hope that this provides you with enough information to get started with PiMP. We welcome any bug reports, suggestions and comments. Good luck with PiMP!



[project_management]:{% static "userguide/img/Project_Management.png" %}
[my_projects]:{% static "userguide/img/My_Projects.png" %}
[create_project]:{% static "userguide/img/Create_Project_Button.png" %}
[project_dialog]:{% static "userguide/img/Create_project_dialog.png" %}
[project_administration]:{% static "userguide/img/project_administration.png" %}
[project_card]:{% static "userguide/img/Project_Card.png" %}
[calibration_samples]:{% static "userguide/img/calibration_samples.png" %}
[assign_calibration_samples]:{% static "userguide/img/Assign_Calibration_samples.png" %}
[assign_qc]:{% static "userguide/img/assign_qc.png" %}
[search_calib]:{% static "userguide/img/search_calib.png" %}
[upload_files]:{% static "userguide/img/upload_files.png" %}
[experiment_definition]:{% static "userguide/img/experiment_definition.png" %}
[analysis_definition]:{% static "userguide/img/analysis_definition.png" %}
[analysis_list]:{% static "userguide/img/analysis_list.png" %}
[loading_screen]:{% static "userguide/img/loading_screen.png" %}
[summary_page]:{% static "userguide/img/Summary_page.png" %}
[pca]:{% static "userguide/img/pca.png" %}
[tic]:{% static "userguide/img/TIC.png" %}
[results]:{% static "userguide/img/results.png" %}
[volcano]:{% static "userguide/img/volcano.png" %}
[metabolites]:{% static "userguide/img/Metabolites.png" %}
[metabolite_peak]:{% static "userguide/img/metabolite_peak.png" %}
[metabolite_int]:{% static "userguide/img/metabolite_int.png" %}
[maps]:{% static "userguide/img/maps.png" %}
[kegg_map]:{% static "userguide/img/maps_kegg.png" %}
[maps_button]:{% static "userguide/img/maps_kegg_button.png" %}
[maps_select_comp]:{% static "userguide/img/maps_select_comp.png" %}
[maps_comparison]:{% static "userguide/img/maps_comparison.png" %}
[comparison]:{% static "userguide/img/comparison.png" %}
[comparison_sidebar]:{% static "userguide/img/comparison_sidebar.png" %}
[peaks]:{% static "userguide/img/peaks.png" %}
[more_comparison]:{% static "userguide/img/more_comparison.png" %}
[more_comparison_filters]:{% static "userguide/img/more_comparison_filters.png" %}
[more_comparison_id_filters]:{% static "userguide/img/more_comparison_id_filters.png" %}
