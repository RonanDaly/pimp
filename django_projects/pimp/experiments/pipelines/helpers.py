import os

from rpy2.robjects import pandas2ri
import pandas as pd

from pimp.settings import getString, getNeededString

import logging

logger = logging.getLogger(__name__)


def get_pimp_wd(project_id):
    base_dir = getNeededString('PIMP_BASE_DIR')
    defined_media_root = os.path.join(base_dir, '..', 'pimp_data')
    media_root = getString('PIMP_MEDIA_ROOT', defined_media_root)
    data_dir = os.path.join(media_root, 'projects')
    project_dir = os.path.join(data_dir, str(project_id))

    logger.info('Data dir: %s', data_dir)
    logger.info('Project dir: %s', project_dir)

    return project_dir


def convert_to_dataframe(factors):

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
