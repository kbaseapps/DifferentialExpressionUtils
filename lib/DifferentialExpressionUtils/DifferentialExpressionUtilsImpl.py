# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import time
import glob
from datetime import datetime

from pprint import pprint
from pprint import pformat

from DataFileUtil.DataFileUtilClient import DataFileUtil
from DataFileUtil.baseclient import ServerError as DFUError
from Workspace.WorkspaceClient import Workspace
from Workspace.baseclient import ServerError as WorkspaceError
#END_HEADER


class DifferentialExpressionUtils:
    '''
    Module Name:
    DifferentialExpressionUtils

    Module Description:
    A KBase module: DifferentialExpressionUtils
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbaseapps/DifferentialExpressionUtils.git"
    GIT_COMMIT_HASH = "c6e863f81fe44459e1c7ae201a8c1105e9887cc7"

    #BEGIN_CLASS_HEADER

    PARAM_IN_SRC_DIR = 'source_dir'
    PARAM_IN_SRC_REF = 'source_ref'
    PARAM_IN_DST_REF = 'destination_ref'
    PARAM_IN_TOOL_USED = 'tool_used'
    PARAM_IN_TOOL_VER = 'tool_version'
    PARAM_IN_EXPR_SET_REF = 'expressionSet_ref'

    def log(self, message, prefix_newline=False):
        print(('\n' if prefix_newline else '') +
              str(time.time()) + ': ' + message)

    def _check_required_param(self, in_params, param_list):
        """
        Check if each of the params in the list are in the input params
        """
        for param in param_list:
            if (param not in in_params or not in_params[param]):
                raise ValueError('{} parameter is required'.format(param))

    def _proc_ws_obj_params(self, ctx, params):
        """
        Check the validity of workspace and object params and return them
        """
        dst_ref = params.get(self.PARAM_IN_DST_REF)

        ws_name_id, obj_name_id = os.path.split(dst_ref)

        if not bool(ws_name_id.strip()) or ws_name_id == '/':
            raise ValueError("Workspace name or id is required in " + self.PARAM_IN_DST_REF)

        if not bool(obj_name_id.strip()):
            raise ValueError("Object name or id is required in " + self.PARAM_IN_DST_REF)

        dfu = DataFileUtil(self.callback_url)

        if not isinstance(ws_name_id, int):

            try:
                ws_name_id = dfu.ws_name_to_id(ws_name_id)
            except DFUError as se:
                prefix = se.message.split('.')[0]
                raise ValueError(prefix)

        self.log('Obtained workspace name/id ' + str(ws_name_id))

        return ws_name_id, obj_name_id

    def _proc_upload_diffexpr_params(self, ctx, params):
        """
        Check the presence and validity of upload expression params
        """
        self._check_required_param(params, [self.PARAM_IN_DST_REF,
                                            self.PARAM_IN_SRC_DIR,
                                            self.PARAM_IN_EXPR_SET_REF,
                                            self.PARAM_IN_TOOL_USED,
                                            self.PARAM_IN_TOOL_VER,
                                            ])

        ws_name_id, obj_name_id = self._proc_ws_obj_params(ctx, params)

        source_dir = params.get(self.PARAM_IN_SRC_DIR)

        if not (os.path.isdir(source_dir)):
            raise ValueError('Source directory does not exist: ' + source_dir)

        if not os.listdir(source_dir):
            raise ValueError('Source directory is empty: ' + source_dir)

        return ws_name_id, obj_name_id, source_dir

    def _get_ws_info(self, obj_ref):

        ws = Workspace(self.ws_url)
        try:
            info = ws.get_object_info_new({'objects': [{'ref': obj_ref}]})[0]
        except WorkspaceError as wse:
            self.log('Logging workspace exception')
            self.log(str(wse))
            raise
        return info

    def _get_diffexpr_data(self, expressionset_ref):
        """
        Get data from expressionset object required to create
        differential expression object
        """
        expression_set = self.ws_client.get_objects2(
                            {'objects': [{'ref': expressionset_ref}]})['data'][0]
        expression_set_data = expression_set['data']

        diffexpr_data = {}
        diffexpr_data['expressionSet_id'] = expressionset_ref
        diffexpr_data['alignmentSet_id'] = expression_set_data.get('alignmentSet_id')
        diffexpr_data['sampleset_id'] = expression_set_data.get('sampleset_id')
        diffexpr_data['genome_id'] = expression_set_data.get('genome_id')

        condition = []

        mapped_expr_ids = expression_set_data.get('mapped_expression_ids')

        for i in mapped_expr_ids:
            for alignment_id, expression_id in i.items():
                expression_data = self.ws_client.get_objects2(
                        {'objects':
                         [{'ref': expression_id}]})['data'][0]['data']
                condition.append(expression_data.get('condition'))

        diffexpr_data.update({'condition': condition})
        return diffexpr_data

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.scratch = config['scratch']
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.ws_url = config['workspace-url']
        self.ws_client = Workspace(self.ws_url)
        self.dfu = DataFileUtil(self.callback_url)
        #END_CONSTRUCTOR
        pass


    def upload_differentialExpression(self, ctx, params):
        """
        Uploads the differential expression  *
        :param params: instance of type "UploadDifferentialExpressionParams"
           (*    Required input parameters for uploading Differential
           expression data string   destination_ref        -   object
           reference of Differential expression data. The object ref is
           'ws_name_or_id/obj_name_or_id' where ws_name_or_id is the
           workspace name or id and obj_name_or_id is the object name or id
           string   source_dir             -   directory with the files to be
           uploaded string   expressionSet_ref      -   expressionSet object
           reference string   tool_used              -   cufflinks, ballgown
           or deseq string   tool_version           -   version of the tool
           used *) -> structure: parameter "destination_ref" of String,
           parameter "source_dir" of String, parameter "expressionSet_ref" of
           String, parameter "tool_used" of String, parameter "tool_version"
           of String
        :returns: instance of type "UploadDifferentialExpressionOutput" (*   
           Output from upload differential expression    *) -> structure:
           parameter "obj_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN upload_differentialExpression

        self.log('Starting upload differential expression, parsing parameters ')
        pprint(params)

        ws_name_id, obj_name_id, source_dir = self._proc_upload_diffexpr_params(ctx, params)

        handle = self.dfu.file_to_shock({'file_path': source_dir,
                                         'make_handle': 1,
                                         'pack': 'zip'
                                          })['handle']

        diff_expression_data = self._get_diffexpr_data(params.get(self.PARAM_IN_EXPR_SET_REF))
        diff_expression_data.update({'file': handle})
        diff_expression_data.update({'tool_used': params.get(self.PARAM_IN_TOOL_USED)})
        diff_expression_data.update({'tool_version': params.get(self.PARAM_IN_TOOL_VER)})

        res = self.ws_client.save_objects({'id': ws_name_id,
                                            "objects": [{
                                                    "type": "KBaseRNASeq.RNASeqDifferentialExpression",
                                                    "data": diff_expression_data,
                                                    "name": obj_name_id
                                                    }]
                                            })[0]
        self.log('save complete')

        returnVal = {'obj_ref': str(res[6]) + '/' + str(res[0]) + '/' + str(res[4])}

        print('Uploaded object: ')
        print(returnVal)
        #END upload_differentialExpression

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method upload_differentialExpression return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def download_differentialExpression(self, ctx, params):
        """
        Downloads expression *
        :param params: instance of type
           "DownloadDifferentialExpressionParams" (* Required input
           parameters for downloading Differential expression string
           source_ref         -       object reference of expression source.
           The object ref is 'ws_name_or_id/obj_name_or_id' where
           ws_name_or_id is the workspace name or id and obj_name_or_id is
           the object name or id *) -> structure: parameter "source_ref" of
           String
        :returns: instance of type "DownloadDifferentialExpressionOutput" (* 
           The output of the download method.  *) -> structure: parameter
           "ws_id" of String, parameter "destination_dir" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN download_differentialExpression

        self.log('Running download_differentialExpression with params:\n' +
                 pformat(params))

        inref = params.get(self.PARAM_IN_SRC_REF)
        if not inref:
            raise ValueError('{} parameter is required'.format(self.PARAM_IN_SRC_REF))

        info = self._get_ws_info(inref)

        obj_ref = str(info[6]) + '/' + str(info[0])

        try:
            expression = self.dfu.get_objects({'object_refs': [obj_ref]})['data']
        except DFUError as e:
            self.log('Logging stacktrace from workspace exception:\n' + e.data)
            raise

        # set the output dir
        timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds() * 1000)
        output_dir = os.path.join(self.scratch, 'download_' + str(timestamp))
        os.mkdir(output_dir)

        file_ret = self.dfu.shock_to_file({
            'shock_id': expression[0]['data']['file']['id'],
            'file_path': output_dir,
            'unpack': 'unpack'
        })

        if not os.listdir(output_dir):
            raise ValueError('No files were downloaded: ' + output_dir)

        for f in glob.glob(output_dir + '/*.zip'):
            os.remove(f)

        returnVal = {'ws_id': info[6],
                     'destination_dir': output_dir}

        #END download_differentialExpression

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method download_differentialExpression return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def export_differentialExpression(self, ctx, params):
        """
        Wrapper function for use by in-narrative downloaders to download expressions from shock *
        :param params: instance of type "ExportParams" (* Required input
           parameters for exporting expression string   source_ref         - 
           object reference of Differential expression. The object ref is
           'ws_name_or_id/obj_name_or_id' where ws_name_or_id is the
           workspace name or id and obj_name_or_id is the object name or id
           *) -> structure: parameter "source_ref" of String
        :returns: instance of type "ExportOutput" -> structure: parameter
           "shock_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN export_differentialExpression

        inref = params.get(self.PARAM_IN_SRC_REF)
        if not inref:
            raise ValueError(self.PARAM_IN_SRC_REF + ' parameter is required')

        info = self._get_ws_info(inref)

        obj_ref = str(info[6]) + '/' + str(info[0])

        try:
            expression = self.dfu.get_objects({'object_refs': [obj_ref]})['data']
        except DFUError as e:
            self.log('Logging stacktrace from workspace exception:\n' + e.data)
            raise

        output = {'shock_id': expression[0]['data']['file']['id']}

        #END export_differentialExpression

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method export_differentialExpression return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
