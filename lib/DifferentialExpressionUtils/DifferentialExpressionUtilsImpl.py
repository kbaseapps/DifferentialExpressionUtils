# -*- coding: utf-8 -*-
#BEGIN_HEADER
import errno
import glob
import logging
import os
import uuid
from datetime import datetime
from pprint import pformat
from pprint import pprint

from DifferentialExpressionUtils.core.diffExprMatrix_utils import GenDiffExprMatrix
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace
from installed_clients.baseclient import ServerError as DFUError
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
    VERSION = "0.1.0"
    GIT_URL = "https://github.com/Tianhao-Gu/DifferentialExpressionUtils.git"
    GIT_COMMIT_HASH = "2573061422c9733b76741707432174fc1d2fd85e"

    #BEGIN_CLASS_HEADER

    PARAM_IN_SRC_DIR = 'source_dir'
    PARAM_IN_SRC_REF = 'source_ref'
    PARAM_IN_DST_REF = 'destination_ref'
    PARAM_IN_TOOL_USED = 'tool_used'
    PARAM_IN_TOOL_VER = 'tool_version'
    PARAM_IN_EXPR_SET_REF = 'expressionset_ref'
    PARAM_IN_GENOME_REF = 'genome_ref'
    PARAM_IN_DIFFEXP_FILEPATH = 'diffexpr_filepath'
    PARAM_IN_DIFFEXP_DATA = 'diffexpr_data'

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

        ws_name, obj_name_id = os.path.split(dst_ref)

        if not bool(ws_name.strip()) or ws_name == '/':
            raise ValueError("Workspace name or id is required in " + self.PARAM_IN_DST_REF)

        if not bool(obj_name_id.strip()):
            raise ValueError("Object name or id is required in " + self.PARAM_IN_DST_REF)

        if not isinstance(ws_name, int):

            try:
                ws_id = self.dfu.ws_name_to_id(ws_name)
            except DFUError as se:
                prefix = se.message.split('.')[0]
                raise ValueError(prefix)

        logging.info('Obtained workspace name/id ' + str(ws_id))

        return ws_name, ws_id, obj_name_id

    def _proc_upload_diffexpr_params(self, ctx, params):
        """
        Check the presence and validity of upload expression params
        """
        self._check_required_param(params, [self.PARAM_IN_DST_REF,
                                            self.PARAM_IN_GENOME_REF,
                                            self.PARAM_IN_TOOL_USED,
                                            self.PARAM_IN_TOOL_VER,
                                            self.PARAM_IN_DIFFEXP_FILEPATH
                                            ])

        ws_name, ws_id, obj_name_id = self._proc_ws_obj_params(ctx, params)

        diffexpr_filepath = params.get(self.PARAM_IN_DIFFEXP_FILEPATH)

        if not (os.path.isfile(diffexpr_filepath)):
            raise ValueError('File {} does not exist: '.format(diffexpr_filepath))

        return ws_name, ws_id, obj_name_id

    def _proc_save_diffexpr_params(self, ctx, params):
        """
        Check the presence and validity of upload expression params
        """
        self._check_required_param(params, [self.PARAM_IN_DST_REF,
                                            self.PARAM_IN_GENOME_REF,
                                            self.PARAM_IN_TOOL_USED,
                                            self.PARAM_IN_TOOL_VER,
                                            self.PARAM_IN_DIFFEXP_DATA
                                            ])

        ws_name, ws_id, obj_name_id = self._proc_ws_obj_params(ctx, params)

        for deFile in params.get(self.PARAM_IN_DIFFEXP_DATA):
            diffexpr_filepath = deFile.get('diffexpr_filepath')

            if not (os.path.isfile(diffexpr_filepath)):
                raise ValueError('File {} does not exist: '.format(diffexpr_filepath))

        return ws_name, ws_id, obj_name_id

    def _get_ws_info(self, obj_ref):

        ws = Workspace(self.ws_url)
        return ws.get_object_info_new({'objects': [{'ref': obj_ref}]})[0]

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
        self.demu = GenDiffExprMatrix(config)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
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
           string   diffexpr_filepath      -   file path of the differential
           expression data file created by cuffdiff, deseq or ballgown string
           tool_used              -   cufflinks, ballgown or deseq string  
           tool_version           -   version of the tool used string  
           genome_ref             -   genome object reference *) ->
           structure: parameter "destination_ref" of String, parameter
           "diffexpr_filepath" of String, parameter "tool_used" of String,
           parameter "tool_version" of String, parameter "genome_ref" of
           String, parameter "description" of String, parameter "type" of
           String, parameter "scale" of String
        :returns: instance of type "UploadDifferentialExpressionOutput" (*   
           Output from upload differential expression    *) -> structure:
           parameter "diffExprMatrixSet_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN upload_differentialExpression

        logging.info('Starting upload differential expression, parsing parameters ')
        pprint(params)

        ws_name, ws_id, obj_name_id = self._proc_upload_diffexpr_params(ctx, params)

        # add more to params to pass on to create diff expr matrix

        params['ws_name'] = ws_name
        params['ws_id'] = ws_id
        params['obj_name'] = obj_name_id

        demset_ref = self.demu.gen_diffexpr_matrices(params)

        logging.info('Differential Expression Matrix set ref: ')
        pprint(demset_ref)

        returnVal = {'diffExprMatrixSet_ref': demset_ref}

        print('Uploaded object: ')
        print(returnVal)
        #END upload_differentialExpression

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method upload_differentialExpression return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def save_differential_expression_matrix_set(self, ctx, params):
        """
        Uploads the differential expression  *
        :param params: instance of type "SaveDiffExprMatrixSetParams" (*   
           Required input parameters for saving Differential expression data
           string   destination_ref         -  object reference of
           Differential expression data. The object ref is
           'ws_name_or_id/obj_name_or_id' where ws_name_or_id is the
           workspace name or id and obj_name_or_id is the object name or id
           list<DiffExprFile> diffexpr_data -  list of DiffExprFiles
           (condition pair & file) string   tool_used               - 
           cufflinks, ballgown or deseq string   tool_version            - 
           version of the tool used string   genome_ref              - 
           genome object reference *) -> structure: parameter
           "destination_ref" of String, parameter "diffexpr_data" of list of
           type "DiffExprFile"
           (------------------------------------------------------------------
           ---------------) -> structure: parameter "condition_mapping" of
           mapping from String to String, parameter "diffexpr_filepath" of
           String, parameter "delimiter" of String, parameter "tool_used" of
           String, parameter "tool_version" of String, parameter "genome_ref"
           of String, parameter "description" of String, parameter "type" of
           String, parameter "scale" of String
        :returns: instance of type "SaveDiffExprMatrixSetOutput" (*    
           Output from upload differential expression    *) -> structure:
           parameter "diffExprMatrixSet_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN save_differential_expression_matrix_set

        logging.info('Starting save differential expression matrix set, parsing parameters ')
        pprint(params)

        ws_name, ws_id, obj_name_id = self._proc_save_diffexpr_params(ctx, params)

        # add the following to params to pass on to create diff expr matrix

        params['ws_name'] = ws_name
        params['ws_id'] = ws_id
        params['obj_name'] = obj_name_id

        demset_ref = self.demu.save_diffexpr_matrices(params)

        logging.info('Differential Expression Matrix set ref: ')
        pprint(demset_ref)

        returnVal = {'diffExprMatrixSet_ref': demset_ref}

        print('Saved object: ')
        print(returnVal)

        #END save_differential_expression_matrix_set

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method save_differential_expression_matrix_set return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def download_differentialExpression(self, ctx, params):
        """
        Downloads expression *
        :param params: instance of type
           "DownloadDifferentialExpressionParams" (* Required input
           parameters for downloading Differential expression string 
           source_ref   -      object reference of expression source. The
           object ref is 'ws_name_or_id/obj_name_or_id' where ws_name_or_id
           is the workspace name or id and obj_name_or_id is the object name
           or id *) -> structure: parameter "source_ref" of String
        :returns: instance of type "DownloadDifferentialExpressionOutput" (* 
           The output of the download method.  *) -> structure: parameter
           "destination_dir" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN download_differentialExpression

        logging.info('Running download_differentialExpression with params:\n' +
                 pformat(params))

        inref = params.get(self.PARAM_IN_SRC_REF)
        if not inref:
            raise ValueError('{} parameter is required'.format(self.PARAM_IN_SRC_REF))

        expression = self.dfu.get_objects({'object_refs': [inref]})['data']

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

        returnVal = {'destination_dir': output_dir}

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

        expression = self.dfu.get_objects({'object_refs': [inref]})['data']

        output = {'shock_id': expression[0]['data']['file']['id']}

        #END export_differentialExpression

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method export_differentialExpression return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def export_diff_expr_matrix_as_tsv(self, ctx, params):
        """
        Export DifferenitalExpressionMatrix object as tsv
        :param params: instance of type "ExportMatrixTSVParams" -> structure:
           parameter "input_ref" of String
        :returns: instance of type "ExportMatrixTSVOutput" -> structure:
           parameter "shock_id" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN export_diff_expr_matrix_as_tsv

        logging.info('Running export_diff_expr_matrix_as_tsv with params:\n' +
                 pformat(params))

        inref = params.get('input_ref')
        if not inref:
            raise ValueError('{} parameter is required'.format('input_ref'))

        diff_expr_obj = self.dfu.get_objects({'object_refs': [inref]})['data'][0]

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        try:
            os.makedirs(output_directory)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(output_directory):
                pass
            else:
                raise

        diff_expr_data = diff_expr_obj['data']
        diff_expr_info = diff_expr_obj['info']
        diff_expr_name = diff_expr_info[1]

        tsv_output = diff_expr_name + '.TSV'

        with open(os.path.join(output_directory, tsv_output), 'w') as output:
            col_ids = diff_expr_data['data']['col_ids']
            row_ids = diff_expr_data['data']['row_ids']
            values = diff_expr_data['data']['values']
            output.write('\t' + '\t'.join(col_ids) + '\n')
            for i, row_id in enumerate(row_ids):
                line = row_id + '\t' + '\t'.join(map(str, values[i])) + '\n'
                output.write(line)

        file_to_shock_params = {
            'file_path': output_directory,
            'pack': 'zip'
        }
        shock_id = self.dfu.file_to_shock(file_to_shock_params)['shock_id']

        returnVal = {'shock_id': shock_id}
        #END export_diff_expr_matrix_as_tsv

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method export_diff_expr_matrix_as_tsv return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
