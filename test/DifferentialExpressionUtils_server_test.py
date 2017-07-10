# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
from datetime import datetime
from distutils.dir_util import copy_tree
import requests
import inspect
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
    def create_expressionset(cls):

        # upload genome object
        genbank_file_name = 'minimal.gbff'
        genbank_file_path = os.path.join(cls.scratch, genbank_file_name)
        shutil.copy(os.path.join('data', genbank_file_name), genbank_file_path)

        genome_object_name = 'test_Genome'
        cls.genome_ref = cls.gfu.genbank_to_genome({'file': {'path': genbank_file_path},
                                                    'workspace_name': cls.wsName,
                                                    'genome_name': genome_object_name
                                                    })['genome_ref']
        # upload reads object
        reads_file_name = 'Sample1.fastq'
        reads_file_path = os.path.join(cls.scratch, reads_file_name)
        shutil.copy(os.path.join('data', reads_file_name), reads_file_path)

        reads_object_name_1 = 'test_Reads_1'
        cls.reads_ref_1 = cls.ru.upload_reads({'fwd_file': reads_file_path,
                                               'wsname': cls.wsName,
                                               'sequencing_tech': 'Unknown',
                                               'interleaved': 0,
                                               'name': reads_object_name_1
                                               })['obj_ref']

        reads_object_name_2 = 'test_Reads_2'
        cls.reads_ref_2 = cls.ru.upload_reads({'fwd_file': reads_file_path,
                                               'wsname': cls.wsName,
                                               'sequencing_tech': 'Unknown',
                                               'interleaved': 0,
                                               'name': reads_object_name_2
                                               })['obj_ref']

        reads_object_name_3 = 'test_Reads_3'
        cls.reads_ref_3 = cls.ru.upload_reads({'fwd_file': reads_file_path,
                                               'wsname': cls.wsName,
                                               'sequencing_tech': 'Unknown',
                                               'interleaved': 0,
                                               'name': reads_object_name_3
                                               })['obj_ref']
        # upload alignment object
        alignment_file_name = 'accepted_hits.bam'
        # alignment_file_name = 'Ath_WT_R1.fastq.sorted.bam'
        alignment_file_path = os.path.join(cls.scratch, alignment_file_name)
        shutil.copy(os.path.join('data', alignment_file_name), alignment_file_path)

        alignment_object_name_1 = 'test_Alignment_1'
        cls.condition_1 = 'test_condition_1'
        cls.alignment_ref_1 = cls.rau.upload_alignment(
            {'file_path': alignment_file_path,
             'destination_ref': cls.wsName + '/' + alignment_object_name_1,
             'read_library_ref': cls.reads_ref_1,
             'condition': cls.condition_1,
             'library_type': 'single_end',
             'assembly_or_genome_ref': cls.genome_ref
             })['obj_ref']

        alignment_object_name_2 = 'test_Alignment_2'
        cls.condition_2 = 'test_condition_2'
        cls.alignment_ref_2 = cls.rau.upload_alignment(
            {'file_path': alignment_file_path,
             'destination_ref': cls.wsName + '/' + alignment_object_name_2,
             'read_library_ref': cls.reads_ref_2,
             'condition': cls.condition_2,
             'library_type': 'single_end',
             'assembly_or_genome_ref': cls.genome_ref
             })['obj_ref']

        alignment_object_name_3 = 'test_Alignment_3'
        cls.condition_3 = 'test_condition_3'
        cls.alignment_ref_3 = cls.rau.upload_alignment(
            {'file_path': alignment_file_path,
             'destination_ref': cls.wsName + '/' + alignment_object_name_3,
             'read_library_ref': cls.reads_ref_3,
             'condition': cls.condition_3,
             'library_type': 'single_end',
             'assembly_or_genome_ref': cls.genome_ref,
             'library_type': 'single_end'
             })['obj_ref']

        # upload sample_set object
        workspace_id = cls.dfu.ws_name_to_id(cls.wsName)
        sample_set_object_name = 'test_Sample_Set'
        sample_set_data = {
            'sampleset_id': sample_set_object_name,
            'sampleset_desc': 'test sampleset object',
            'Library_type': 'SingleEnd',
            'condition': [cls.condition_1, cls.condition_2, cls.condition_3],
            'domain': 'Unknown',
            'num_samples': 3,
            'platform': 'Unknown'}
        save_object_params = {
            'id': workspace_id,
            'objects': [{
                'type': 'KBaseRNASeq.RNASeqSampleSet',
                'data': sample_set_data,
                'name': sample_set_object_name
            }]
        }

        dfu_oi = cls.dfu.save_objects(save_object_params)[0]
        cls.sample_set_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

        # upload alignment_set object
        object_type = 'KBaseRNASeq.RNASeqAlignmentSet'
        alignment_set_object_name = 'test_Alignment_Set'
        alignment_set_data = {
            'genome_id': cls.genome_ref,
            'read_sample_ids': [reads_object_name_1,
                                reads_object_name_2,
                                reads_object_name_3],
            'mapped_rnaseq_alignments': [{reads_object_name_1: alignment_object_name_1},
                                         {reads_object_name_2: alignment_object_name_2},
                                         {reads_object_name_3: alignment_object_name_3}],
            'mapped_alignments_ids': [{reads_object_name_1: cls.alignment_ref_1},
                                      {reads_object_name_2: cls.alignment_ref_2},
                                      {reads_object_name_3: cls.alignment_ref_3}],
            'sample_alignments': [cls.alignment_ref_1,
                                  cls.alignment_ref_2,
                                  cls.alignment_ref_3],
            'sampleset_id': cls.sample_set_ref}
        save_object_params = {
            'id': workspace_id,
            'objects': [{
                'type': object_type,
                'data': alignment_set_data,
                'name': alignment_set_object_name
            }]
        }

        dfu_oi = cls.dfu.save_objects(save_object_params)[0]
        cls.alignment_set_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

        # upload expression_set object
        cls.expressionset_ref = cls.stringtie.run_stringtie_app(
            {'alignment_object_ref': cls.alignment_set_ref,
             'workspace_name': cls.wsName,
             "min_read_coverage": 2.5,
             "junction_base": 10,
             "num_threads": 3,
             "min_isoform_abundance": 0.1,
             "min_length": 200,
             "skip_reads_with_no_ref": 1,
             "merge": 0,
             "junction_coverage": 1,
             "ballgown_mode": 1,
             "min_locus_gap_sep_value": 50,
             "disable_trimming": 1})['expression_obj_ref']

    @classmethod
    def setupTestData(cls):
        """
        sets up files for upload
        """
        timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds() * 1000)

        cls.upload_cuffdiff2_dir = 'upload_cuffdiff2_' + str(timestamp)
        cls.upload_cuffdiff2_dir_path = os.path.join(cls.scratch, cls.upload_cuffdiff2_dir)
        cls.uploaded_cuffdiff2_zip = cls.upload_cuffdiff2_dir + '.zip'

        cls.upload_cuffdiff3_dir = 'upload_cuffdiff3_' + str(timestamp)
        cls.upload_cuffdiff3_dir_path = os.path.join(cls.scratch, cls.upload_cuffdiff3_dir)
        cls.uploaded_cuffdiff3_zip = cls.upload_cuffdiff3_dir + '.zip'

        cls.upload_deseq_dir = 'upload_deseq_' + str(timestamp)
        cls.upload_deseq_dir_path = os.path.join(cls.scratch, cls.upload_deseq_dir)
        cls.uploaded_deseq_zip = cls.upload_deseq_dir + '.zip'

        cls.upload_ballgown_dir = 'upload_ballgown_' + str(timestamp)
        cls.upload_ballgown_dir_path = os.path.join(cls.scratch, cls.upload_ballgown_dir)
        cls.uploaded_ballgown_zip = cls.upload_ballgown_dir + '.zip'

        copy_tree('data/cuffdiff_output_2conditions', cls.upload_cuffdiff2_dir_path)
        copy_tree('data/cuffdiff_output_3conditions', cls.upload_cuffdiff3_dir_path)
        copy_tree('data/deseq_output', cls.upload_deseq_dir_path)
        copy_tree('data/ballgown_output', cls.upload_ballgown_dir_path)

        cls.narrative_expressionset_ref = '4389/18/2'

        #cls.expressionset_ref = cls.create_expressionset()

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa

    def test_upload_cuffdiff_differentialExpression(self):

        params = {
                  'destination_ref': self.getWsName() + '/test_cuffdiff_diffexp',
                  'source_dir': self.upload_cuffdiff2_dir_path,
                  'expressionset_ref': self.narrative_expressionset_ref,
                  'tool_used': 'cuffdiff',
                  'tool_version': '2.2.1',
                  'diffexpr_filename': 'gene_exp_deleted_cols.csv'
                  }
        retVal = self.getImpl().upload_differentialExpression(self.ctx, params)[0]

        inputObj = self.dfu.get_objects(
            {'object_refs': [self.narrative_expressionset_ref]})['data'][0]

        print("============ INPUT EXPRESSION SET OBJECT ==============")
        pprint(inputObj)
        print("==========================================================")

        obj = self.dfu.get_objects(
            {'object_refs': [retVal.get('diffexpr_obj_ref')]})['data'][0]

        print("============ DIFFERENTIAL EXPRESSION OUTPUT ==============")
        pprint(obj)
        print("==========================================================")

        self.assertEqual(obj['info'][2].startswith('KBaseRNASeq.RNASeqDifferentialExpression'), True)
        d = obj['data']
        self.assertEqual(d['genome_id'], inputObj['data']['genome_id'])
        self.assertEqual(d['expressionSet_id'], self.narrative_expressionset_ref)
        self.assertEqual(d['alignmentSet_id'], inputObj['data']['alignmentSet_id'])
        self.assertEqual(d['sampleset_id'], inputObj['data']['sampleset_id'])

    def test_upload_deseq_differentialExpression(self):

        params = {
                  'destination_ref': self.getWsName() + '/test_deseq_diffexp',
                  'source_dir': self.upload_deseq_dir_path,
                  'expressionset_ref': self.narrative_expressionset_ref,
                  'tool_used': 'deseq',
                  'tool_version': 'deseq_version',
                  'diffexpr_filename': 'sig_genes_results.csv'
                  }
        retVal = self.getImpl().upload_differentialExpression(self.ctx, params)[0]

        inputObj = self.dfu.get_objects(
            {'object_refs': [self.narrative_expressionset_ref]})['data'][0]

        print("============ INPUT EXPRESSION SET OBJECT ==============")
        pprint(inputObj)
        print("==========================================================")

        obj = self.dfu.get_objects(
            {'object_refs': [retVal.get('diffexpr_obj_ref')]})['data'][0]

        print("============ DIFFERENTIAL EXPRESSION OUTPUT ==============")
        pprint(obj)
        print("==========================================================")

    def test_upload_ballgown_differentialExpression(self):

        params = {
                  'destination_ref': self.getWsName() + '/test_ballgown_diffexp',
                  'source_dir': self.upload_ballgown_dir_path,
                  'expressionset_ref': self.narrative_expressionset_ref,
                  'tool_used': 'ballgown',
                  'tool_version': 'ballgown_version',
                  'diffexpr_filename': 'ballgown_expmat.tsv'
                  }
        retVal = self.getImpl().upload_differentialExpression(self.ctx, params)[0]

        inputObj = self.dfu.get_objects(
            {'object_refs': [self.narrative_expressionset_ref]})['data'][0]

        print("============ INPUT EXPRESSION SET OBJECT ==============")
        pprint(inputObj)
        print("==========================================================")

        obj = self.dfu.get_objects(
            {'object_refs': [retVal.get('diffexpr_obj_ref')]})['data'][0]

        print("============ DIFFERENTIAL EXPRESSION OUTPUT ==============")
        pprint(obj)
        print("==========================================================")

    
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
                                    'source_dir': self.upload_cuffdiff_dir_path,
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                  },
                                  'destination_ref parameter is required')

    def test_upload_fail_no_ws_name(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': '/foo',
                                    'source_dir': self.upload_cuffdiff_dir_path,
                                    'expressionset_ref': self.narrative_expressionset_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                   },
                                   'Workspace name or id is required in destination_ref')

    def test_upload_fail_no_obj_name(self):
        self.fail_upload_diffexpr({
                                    'destination_ref': self.getWsName() + '/',
                                    'source_dir': self.upload_cuffdiff_dir_path,
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
                                    'source_dir': self.upload_cuffdiff_dir_path,
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
                                    'source_dir': self.upload_cuffdiff_dir_path,
                                    'expressionset_ref': self.genome_ref,
                                    'tool_used': 'cuffdiff',
                                    'tool_version': '2.2.1',
                                    'diffexpr_filename': 'gene_exp.diff'
                                  },
            '"expressionset_ref" should be of type KBaseRNASeq.RNASeqExpressionSet',
            exception=TypeError)



