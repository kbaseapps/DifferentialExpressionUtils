# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
from datetime import datetime
from distutils.dir_util import copy_tree
import requests

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from DataFileUtil.DataFileUtilClient import DataFileUtil
from DifferentialExpressionUtils.DifferentialExpressionUtilsImpl import DifferentialExpressionUtils
from DifferentialExpressionUtils.DifferentialExpressionUtilsServer import MethodContext
from DifferentialExpressionUtils.authclient import KBaseAuth as _KBaseAuth


class DifferentialExpressionUtilsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('DifferentialExpressionUtils'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'DifferentialExpressionUtils',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = DifferentialExpressionUtils(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.dfu = DataFileUtil(cls.callback_url)
        cls.setupTestData()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_DifferentialExpressionUtils_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    @classmethod
    def setupTestData(cls):
        """
        sets up files for upload
        """
        timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds() * 1000)
        cls.upload_dir = 'upload_' + str(timestamp)
        cls.upload_dir_path = os.path.join(cls.scratch, cls.upload_dir)
        cls.uploaded_zip = cls.upload_dir + '.zip'

        copy_tree('data/cuffdiff_output', cls.upload_dir_path)

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_upload_differentialExpression(self):

        params = {
                  'destination_ref': self.getWsName() + '/test_output_diffexp',
                  'source_dir': self.upload_dir_path,
                  'expressionSet_ref': '22254/32/1',
                  'tool_used': 'cuffdiff',
                  'tool_version': '2.2.1'
                  }

        retVal = self.getImpl().upload_differentialExpression(self.ctx, params)[0]

        inputObj = self.dfu.get_objects(
            {'object_refs': ['22254/32/1']})['data'][0]

        print("============ INPUT EXPRESSION SET OBJECT ==============")
        pprint(inputObj)
        print("==========================================================")

        obj = self.dfu.get_objects(
            {'object_refs': [retVal.get('obj_ref')]})['data'][0]

        print("============ DIFFERENTIAL EXPRESSION OUTPUT ==============")
        pprint(obj)
        print("==========================================================")

        self.assertEqual(obj['info'][2].startswith('KBaseRNASeq.RNASeqDifferentialExpression'), True)
        d = obj['data']
        self.assertEqual(d['genome_id'], inputObj['data']['genome_id'])
        self.assertEqual(d['expressionSet_id'], '22254/32/1')
        self.assertEqual(d['alignmentSet_id'], inputObj['data']['alignmentSet_id'])
        self.assertEqual(d['sampleset_id'], inputObj['data']['sampleset_id'])
