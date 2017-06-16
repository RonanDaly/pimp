import threading
import logging
import inspect


class ContextLocal(threading.local):
    project = 0
    analysis = 0
    user = 0

class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
            cls.instance.cl = ContextLocal()
        return cls.instance

    def attach_analysis(self, analysis_id):
        self.cl.analysis = analysis_id

    def attach_project(self, project_id):
        self.cl.project = project_id

    def attach_user(self, user_id):
        self.cl.user = user_id

    def detach(self):
        self.cl.analysis = 0
        self.cl.project = 0
        self.cl.user = 0

    def filter(self, record):
        record.project = self.cl.project
        record.analysis = self.cl.analysis
        record.user = self.cl.user
        return True

    def __init__(self):
        super(ContextFilter, self).__init__()


def attach_detach_logging_info(func):
    argspec = inspect.getargspec(func)
    project_id_pos = argspec.args.index('project_id') if 'project_id' in argspec.args else None
    analysis_id_pos = argspec.args.index('analysis_id') if 'analysis_id' in argspec.args else None
    def wrapper(*args, **kwargs):
        if 'project_id' in kwargs:
            ContextFilter.instance.attach_project(kwargs['project_id'])
        elif project_id_pos is not None:
            ContextFilter.instance.attach_project(args[project_id_pos])
        if 'analysis_id' in kwargs:
            ContextFilter.instance.attach_analysis(kwargs['analysis_id'])
        elif analysis_id_pos is not None:
            ContextFilter.instance.attach_analysis(args[analysis_id_pos])
        retval = func(*args, **kwargs)
        ContextFilter.instance.detach()
        return retval
    return wrapper


def detach_logging_info(func):
    def wrapper(*args, **kwargs):
        retval = func(*args, **kwargs)
        ContextFilter.instance.detach()
        return retval
    return wrapper


FINE = 7
FINER = 5
FINEST = 2


class FineLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super(FineLogger, self).__init__(name, level)

        logging.addLevelName(FINE, "FINE")
        logging.addLevelName(FINER, "FINER")
        logging.addLevelName(FINEST, "FINEST")

    def fine(self, msg, *args, **kwargs):
        if self.isEnabledFor(FINE):
            self._log(FINE, msg, args, **kwargs)

    def finer(self, msg, *args, **kwargs):
        if self.isEnabledFor(FINER):
            self._log(FINER, msg, args, **kwargs)

    def finest(self, msg, *args, **kwargs):
        if self.isEnabledFor(FINEST):
            self._log(FINEST, msg, args, **kwargs)
