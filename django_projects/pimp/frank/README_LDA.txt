Claire Thompson. MS2LDA file changes README.
————————————————————————————————————————————

FILES THAT HAVE CHANGED
=======================

1. views.py
- Added a new function - ms2lda_vis - which will be called by URL patterns
  when match is made on ms2lda url. This will get the context dictionary
  and render the ms2lda_vis html.
- Added a new function - get_ms2lda_vis_context - which will build the
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
- Modified fragmentation_set function so that displays the ms2lda form
  if that is the chosen annotation tool
- Modified generate_annotations so that after the annotation has been created
  it calls run_ms2lda_analysis to create the ms2lda object, run the LDA etc.
- Modified set_annotation_query_parameters so that it builds an annotation
  query object containing the parameters entered in ms2lda forms page


2. tasks.py
- Created a new function - run_ms2lda_analysis - which collect relevant
  data and run the LDA
    - Extract the parameters from the annotation query object
    - Extract MS1 peaks from the database and save into pandas dataframe
    - Extract MS2 peaks from the database and save into pandas dataframe
    - Generate MS2 Intensity Matrix and save into pandas dataframe
    - Save data in a ms2lda object
    - Run an LDA analysis on the data (uses existing run_lda method)
    - Run thresholding on the data (uses existing do_thresholding method)
    - Save the ma2lda object to a data file so that it can be used later
      in the visualisation

3. forms.py
- Created a new class - MS2LDAQueryForm - which will display a form allowing
  the user to enter all the parameters - both pre-filtering and LDA Analysis
  parameters

4. urls.py
- Modified the urlpatterns data structure to add a new entry for the mass2lda url

5. lda_for_fragments.py
- Modified the Ms2lda class so there is now an additional attribute -
  mass2motif_count - which holds the number of mass2motif that should be used
  for the annotation

6. fragmentation_set.html
- If annotation tool associated with the annotation is ms2lda then add a ms2lda
  visualisation button which will use url patterns mechanism to generate a ms2lda
  url request

7. define_annotation_query.html
- Updated so if the annotation is being created for ms2lda then the screen format
  is slightly more compressed because of the number of parameters that have to be
  defined for ms2lda.

8. ms2lda_vis.html
- Created his new file to hold the D3/Javascript/ccs/html scripts for the
  Network Graph, MS2 Spectrum plot and Parent Ion plot
- First displays the Fragmentations and annotation details at top of screen
- Network Graph
    - The NetworkX code from the legacy ms2lda (in graph.html) was used as the
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

- lda_for_fragments.py  - ma2lda object(), run_lda(), do_threshold(),
  restore_project(), save_project()
- d3.min.js - copy of the D3 library needs to be placed in django_projects/static/
  since ma2lda_vis.html loads it in from here so that code can be run when
  not connected to the internet
- lda_visualisation.py - get_json_from_docdf()
- FrAnK annotation tool selection. Used PiMP admin permissions to add a new
  annotation tool option - ms2lda.

Note
=====================
Create in your home directory a folder called 'ms2lda_data'. This will hold the LDA project files and also json files.

Enhancements/Defects
=====================

Ms2lda - change forms so that units are displayed
Ms2lda - support sparse matrix
Ms2lda - main graph screen - json workaround for network graph (passed via file
           instead of context dictionary)
Ms2lda - handle losses on both spectra graph and parent ion graph
Ms2lda - grey out annotation screen while annotation is being built
Ms2lda - thresholding only done at time of create annotation
Ms2lda - add annotation name to peak
Ms2lda - parent ion screen - use routine to show split line on graph
Ma2lda - changing min ms2 intensity parameter




