import logging

from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
from rpy2.rinterface import RRuntimeError

logger = logging.getLogger(__name__)


def run_r(function_string, *args, **kwargs):
    try:
        function = robjects.r[function_string]
        return function(*args, **kwargs)
    except RRuntimeError as e:
        try:
            new_e = RRuntimeError(str(e) + '\n' + '\n'.join(robjects.r('unlist(traceback())')))
        except Exception as traceback_exc:
            raise RRuntimeError('An error occurred while getting traceback from R: ' + str(traceback_exc) + '\n' +
                                str(e))
        raise new_e
