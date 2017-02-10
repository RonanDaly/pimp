# This file is required for notebooks that are located in a subfolder to work
# Only when launched from shell_plus --notebook
# See https://github.com/django-extensions/django-extensions/issues/865 for more

# Allows the kernel to "see" the project during initialization. This
# FILE_PATH corresponds to Jupyter's "notebook-dir", but we want notebooks to
# behave as though they resided in the base directory to allow for clean
# imports.
import sys
import os
FILE_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_BASE_PATH = os.path.abspath(os.path.join(FILE_PATH, '..'))
sys.path.insert(1, PROJECT_BASE_PATH)