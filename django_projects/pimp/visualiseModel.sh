#!/bin/bash

# Mangle around the dot file to get the layout needed
# This probably involves putting invisible edges (e.g. data_models_Dataset -> groups_models_SampleAttribute [style=invis])


honcho run python manage.py graph_models -g groups experiments data compound frank projects fileupload -o pimpFrankVisualisation.dot
dot -Tpdf -opimpFrankVisualisation.pdf -Gsize=4.8,2.8\! -Gmargin=0 -Gratio=0.707 -Gdpi=300 pimpFrankVisualisation.dot

honcho run python manage.py graph_models -g groups experiments data compound projects fileupload -o pimpVisualisation.dot
dot -Tpdf -opimpVisualisation.pdf -Gsize=4.8,2.8\! -Gmargin=1 -Gratio=0.707 -Gdpi=300 pimpVisualisation.dot
