import threading
import logging


class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
            cls.instance.tl = threading.local()
            cls.instance.tl.project = 0
            cls.instance.tl.analysis = 0
        return cls.instance

    def attach_analysis(self, analysis_id):
        self.tl.analysis = analysis_id

    def attach_project(self, project_id):
        self.tl.project = project_id

    def filter(self, record):
        record.project = self.tl.project
        record.analysis = self.tl.analysis
        return True

    def __init__(self):
        super(ContextFilter, self).__init__()
