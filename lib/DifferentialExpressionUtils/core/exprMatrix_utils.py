import os
import errno
import csv
import uuid
from datetime import datetime
from collections import namedtuple

from Workspace.WorkspaceClient import Workspace as Workspace
from KBaseFeatureValues.KBaseFeatureValuesClient import KBaseFeatureValues

class GenExprMatrix:

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = os.path.join(config['scratch'], 'DEM_' + str(uuid.uuid4()))
        self.ws_url = config['workspace-url']
        self.fv = KBaseFeatureValues(self.callback_url)
        self._mkdir_p(self.scratch)

    def _mkdir_p(self, path):
        """
        _mkdir_p: make directory for given path
        """
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
    # deseq output

    def gen_expression_matrix(self, params):
        pass
