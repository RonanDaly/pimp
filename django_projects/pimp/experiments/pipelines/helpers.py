import os
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
