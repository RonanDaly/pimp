import threading
import logging


class ContextLocal(threading.local):
    project = 0
    analysis = 0


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

    def filter(self, record):
        record.project = self.cl.project
        record.analysis = self.cl.analysis
        return True

    def __init__(self):
        super(ContextFilter, self).__init__()
