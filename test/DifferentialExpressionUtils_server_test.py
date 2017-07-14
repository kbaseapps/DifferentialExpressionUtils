# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from DataFileUtil.DataFileUtilClient import DataFileUtil
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil
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
        cls.gfu = GenomeFileUtil(cls.callback_url)
        suffix = int(time.time() * 1000)
        cls.wsName = "test_DifferentialExpressionUtils_" + str(suffix)
        cls.wsClient.create_workspace({'workspace': cls.wsName})
        cls.setupTestData()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        return self.__class__.wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    @classmethod
    def setupTestData(cls):

        genbank_file_name = 'minimal.gbff'
        genbank_file_path = os.path.join(cls.scratch, genbank_file_name)
        shutil.copy(os.path.join('data', genbank_file_name), genbank_file_path)

        genome_object_name = 'test_Genome'
        cls.genome_ref = cls.gfu.genbank_to_genome({'file': {'path': genbank_file_path},
                                                    'workspace_name': cls.wsName,
                                                    'genome_name': genome_object_name
                                                    })['genome_ref']

        #cls.narrative_genome_ref = '23837/2/1'

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa

    #@unittest.skip("skipped test_upload_cuffdiff_differentialExpression")
    def test_upload_cuffdiff_differentialExpression(self):

        params = {
                  'destination_ref': self.getWsName() + '/test_cuffdiff_diffexp',
                  'genome_ref': self.genome_ref,
                  'tool_used': 'cuffdiff',
                  'tool_version': '2.2.1',
                  'diffexpr_filepath': 'data/cuffdiff_output_3conditions/gene_exp_inf_small.diff'
                  }
        retVal = self.getImpl().upload_differentialExpression(self.ctx, params)[0]

        obj = self.dfu.get_objects(
            {'object_refs': [retVal.get('diffExprMatrixSet_ref')]})['data'][0]

        print("============ DIFFERENTIAL EXPRESSION MATRIX SET OUTPUT ==============")
        pprint(obj)
        print("==========================================================")

    #@unittest.skip("skipped test_upload_deseq_differentialExpression")
    def test_upload_deseq_differentialExpression(self):

        params = {
                  'destination_ref': self.getWsName() + '/test_deseq_diffexp',
                  'genome_ref': self.genome_ref,
                  'tool_used': 'deseq',
                  'tool_version': 'deseq_version',
                  'diffexpr_filepath': 'data/deseq_output/sig_genes_results_small.csv'
                  }
        retVal = self.getImpl().upload_differentialExpression(self.ctx, params)[0]
        
        obj = self.dfu.get_objects(
            {'object_refs': [retVal.get('diffExprMatrixSet_ref')]})['data'][0]

        print("============ DIFFERENTIAL EXPRESSION MATRIX OUTPUT ==============")
        pprint(obj)
        print("==========================================================")

    #@unittest.skip("skipped test_upload_ballgown_differentialExpression")
    def test_upload_ballgown_differentialExpression(self):

        params = {
                  'destination_ref': self.getWsName() + '/test_ballgown_diffexp',
                  'genome_ref': self.genome_ref,
                  'tool_used': 'ballgown',
                  'tool_version': 'ballgown_version',
                  'diffexpr_filepath': 'data/ballgown_output/ballgown_diffexp_small.tsv'
                  }
        retVal = self.getImpl().upload_differentialExpression(self.ctx, params)[0]

        print('BALL GOWN TEST RETVAL')
        pprint(retVal)

        obj = self.dfu.get_objects(
            {'object_refs': [retVal.get('diffExprMatrixSet_ref')]})['data'][0]

        print("============ DIFFERENTIAL EXPRESSION MATRIX OUTPUT ==============")
        pprint(obj)
        print("==========================================================")

    '''  
    def fail_upload_diffexpr(self, params, error, exception=ValueError, do_startswith=False):

        test_name = inspect.stack()[1][3]
        print('\n*** starting expected upload fail test: ' + test_name + ' **')

        with self.assertRaises(exception) as context:
            self.getImpl().upload_differentialExpression(self.ctx, params)
        if do_startswith:
            self.assertTrue(str(context.exception.message).startswith(error),
                            "Error message {} does not start with {}".format(
                                str(context.exception.message),
                                error))
        else:
            self.assertEqual(error, str(context.exception.message))

    def test_upload_fail_no_dst_ref(self):
        self.fail_upload_diffexpr({
                                    'source_dir': self.upload_cuffdiff2_dir_path,
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                  },
                                  'destination_ref parameter is required')

    def test_upload_fail_no_ws_name(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': '/foo',
                                    'source_dir': self.upload_cuffdiff2_dir_path,
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                   },
                                   'Workspace name or id is required in destination_ref')

    def test_upload_fail_no_obj_name(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': self.getWsName() + '/',
                                    'source_dir': self.upload_cuffdiff2_dir_path,
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                   },
                                   'Object name or id is required in destination_ref')

    def test_upload_fail_no_src_dir(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': self.getWsName() + '/test_diffexpr',
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                  },
                                  'source_dir parameter is required')

    def test_upload_fail_non_existant_src_dir(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': self.getWsName() + '/test_diffexpr',
                                    'source_dir': 'foo',
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                  },
                                  'Source directory does not exist: foo')

    def test_upload_fail_no_diffexpr_filename(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': self.getWsName() + '/test_diffexpr',
                                    'source_dir': self.upload_cuffdiff2_dir_path,
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1'
                                  },
                                  'diffexpr_filename parameter is required')

    def test_upload_fail_bad_wsname(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': '&bad' + '/foo',
                                    'source_dir': 'foo',
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                  },
                                  'Illegal character in workspace name &bad: &')

    def test_upload_fail_non_existant_wsname(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': '1s' + '/foo',
                                    'source_dir': 'foo',
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                  },
                                  'No workspace with name 1s exists')
    
    def test_upload_fail_non_expset_ref(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': self.getWsName() + '/test_diffexpr',
                                    'source_dir': self.upload_cuffdiff2_dir_path,
                                    'expressionset_ref': self.genome_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                  },
            '"expressionset_ref" should be of type KBaseRNASeq.RNASeqExpressionSet',
            exception=TypeError)
    '''


