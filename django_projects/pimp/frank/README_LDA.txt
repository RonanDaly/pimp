Claire Thompson. Mass2LDA file changes README.
————————————————————————————————————————————

FILES THAT HAVE CHANGED 
=======================

1. views.py
- Added a new function - mass2lda_vis - which will be called by URL patterns 
  when match is made on mass2lda url. This will get the context dictionary 
  and render the mass2lda_vis html.
- Added a new function - get_mass2lda_vis_context - which will build the 
  context dictionary
    - Loads the .project file that was saved when the annotation was created
    - Builds the plot data that is needed for MS2 Fragment and Parent ion plots 
      (with call to get_topic_graph_data() )
    - Build the NetworkX data needed for the Network Graph - calls 
      get_json_from_docdf()
    - Returns the context dictionary data structure containing 
      fragment slug name, annotation name, graph data, topic plot data
- Added a new function - get_topic_graph_data - which build the plot data
    - Takes as input docdf, topicdf, ms2 dataframes from the mass2lda object
    - Creates a nested array containing each MS1 peak that is in each mass2motif
    - Creates a nested array containing the full  MS2 Spectra for each MS1 
      peak in the above array
    - Creates a nested array containing the MS2 peaks that belong to each 
      mass2motif
- Modified fragmentation_set function so that displays the mass2lda form 
  if that is the chosen annotation tool
- Modified generate_annotations so that after the annotation has been created 
  it calls run_mass2lda_analysis to create the mass2lda object, run the LDA etc.
- Modified set_annotation_query_parameters so that it builds an annotation 
  query object containing the parameters entered in mass2lda forms page


2. tasks.py
- Created a new function - run_mass2lda_analysis - which collect relevant 
  data and run the LDA
    - Extract the parameters from the annotation query object
    - Extract MS1 peaks from the database and save into pandas dataframe
    - Extract MS2 peaks from the database and save into pandas dataframe
    - Generate MS2 Intensity Matrix and save into pandas dataframe
    - Save data in a mass2lda object
    - Run an LDA analysis on the data (uses existing run_lda method)
    - Run thresholding on the data (uses existing do_thresholding method)
    - Save the mass2lda object to a data file so that it can be used later 
      in the visualisation 

3. forms.py
- Created a new class - Mass2LDAQueryForm - which will display a form allowing 
  the user to enter all the parameters - both pre-filtering and LDA Analysis 
  parameters

4. urls.py
- Modified the urlpatterns data structure to add a new entry for the mass2lda url
 
5. lda_for_fragments.py
- Modified the Ms2lda class so there is now an additional attribute - 
  mass2motif_count - which holds the number of mass2motif that should be used 
  for the annotation
  
6. fragmentation_set.html
- If annotation tool associated with the annotation is mass2lda then add a mass2lda 
  visualisation button which will use url patterns mechanism to generate a mass2lda 
  url request
 
7. define_annotation_query.html
- Updated so if the annotation is being created for mass2lda then the screen format 
  is slightly more compressed because of the number of parameters that have to be 
  defined for mass2lda.

8. mass2lda_vis.html
- Created his new file to hold the D3/Javascript/ccs/html scripts for the 
  Network Graph, MS2 Spectrum plot and Parent Ion plot
- First displays the Fragmentations and annotation details at top of screen
- Network Graph
    - The NetworkX code from the legacy mass2lda (in graph.html) was used as the
      basis of the graph
    - Modified so that reads the plot data in from the context dictionary passed in
      to the html
    - Changed so that if mass2motif is selected on the graph  a call will be made 
      to the function -  display_fragment_spectrum - to update the MS2 Spectrum plot
    - Removed any redundant code that previously interacted with other legacy screens
- MS2 Spectrum plot
    - Created a new function - display_fragment_spectrum - that will display the 
      MS2 Fragment plot
    - Plot data is passed in via the context dictionary
    - After displaying the plot it will call the following function to make the
      relevant updated to the parent ion graph.
- Parent Ion plot
- Created a new function - display_parent_ion_topics_graph - that will display 
  the Parent Ion plot
- Plot data is passed in via the context dictionary


Dependencies
============

- lda_for_fragments.py  - mass2lda object(), run_lda(), do_threshold(), 
  restore_project(), save_project()
- d3.min.js - copy of the D3 library needs to be placed in django_projects/static/ 
  since mass2lda_vis.html loads it in from here so that code can be run when 
  not connected to the internet
- lda_visualisation.py - get_json_from_docdf()
- FrAnK annotation tool selection. Used PiMP admin permissions to add a new 
  annotation tool option - mass2lda. 


Enhancements/Defects
=====================

Mass2lda - change forms so that units are displayed
Mass2lda - support sparse matrix
Mass2lda - main graph screen - json workaround for network graph (passed via file
           instead of context dictionary)
Mass2lda - handle losses on both spectra graph and parent ion graph
Mass2lda - grey out annotation screen while annotation is being built
Mass2lda - thresholding only done at time of create annotation
Mass2lda - add annotation name to peak
Mass2lda - parent ion screen - use routine to show split line on graph
Mass2lda - changing min ms2 intensity parameter 




