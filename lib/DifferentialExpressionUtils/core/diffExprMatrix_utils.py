import csv
import errno
import os
import re
import uuid
from collections import namedtuple
from datetime import datetime
from numpy import log2

from DataFileUtil.DataFileUtilClient import DataFileUtil
from GenomeSearchUtil.GenomeSearchUtilClient import GenomeSearchUtil
from KBaseFeatureValues.KBaseFeatureValuesClient import KBaseFeatureValues
from SetAPI.SetAPIClient import SetAPI
from Workspace.WorkspaceClient import Workspace as Workspace

class GenDiffExprMatrix:

    INVALID_WS_OBJ_NAME_RE = re.compile('[^\\w\\|._-]')

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = os.path.join(config['scratch'], 'DEM_' + str(uuid.uuid4()))
        self.ws_url = config['workspace-url']
        self.ws_client = Workspace(self.ws_url)
        self.fv = KBaseFeatureValues(self.callback_url)
        self.dfu = DataFileUtil(self.callback_url)
        self.setAPI = SetAPI(self.callback_url)
        self.gsu = GenomeSearchUtil(self.callback_url)
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

    def setup_data(self):

        self.new_col_names = ['gene_id', 'log2_fold_change', 'p_value', 'q_value']

    def get_feature_ids(self, genome_ref):
        """
        _get_feature_ids: get feature ids from genome
        """

        feature_num = self.gsu.search({'ref': genome_ref})['num_found']

        genome_features = self.gsu.search({'ref': genome_ref,
                                           'limit': feature_num,
                                           'sort_by': [['feature_id', True]]})['features']

        features_ids = map(lambda genome_feature: genome_feature.get('feature_id'),
                           genome_features)

        return list(set(features_ids))

    def gen_matrix(self, infile, old_col_names, delimiter):
        with open(infile, 'rb') as source:
            rdr = csv.DictReader(source, delimiter=delimiter)
            col_names = self.new_col_names[1:]
            row_names = []
            values = []
            for row in rdr:
                try:
                    values.append([float(row[v]) for v in old_col_names[1:]])
                except:
                    values_list = []
                    for v in old_col_names[1:]:
                        tmpval = row[v]
                        if isinstance(tmpval, (int, long, float)):
                            values_list.append(float(tmpval))
                        elif isinstance(tmpval, basestring):
                            if 'na' in tmpval.lower() or 'none' in tmpval.lower():
                                values_list.append(None)
                            else:
                                tmpval = tmpval.replace("'", "")
                                tmpval = tmpval.replace('"', '')
                                values_list.append(float(tmpval))
                        else:
                            raise ValueError("invalid type in input file: {}".format(tmpval))
                    values.append(values_list)
                row_names.append(row[old_col_names[0]])

        twoD_matrix = { 'row_ids': row_names,
                        'col_ids': col_names,
                        'values': values
                        }

        return twoD_matrix

    def get_max_fold_change_to_handle_inf(self, infile):
        maxvalue = 0
        with open(infile) as source:
            rdr = csv.DictReader(source, dialect='excel-tab')
            for line in rdr:
                log2fc_val = line.get('log2_fold_change')
                if not 'inf' in str(log2fc_val):
                    log2fc = abs(float(log2fc_val))
                    if log2fc > maxvalue:
                        maxvalue = log2fc

            print('maxvalue: ', maxvalue)
            return maxvalue

    def gen_cuffdiff_matrix(self, infile, delimiter='\t'):

        max_value = self.get_max_fold_change_to_handle_inf(infile)
        with open(infile, 'rb') as source:
            rdr = csv.DictReader(source, delimiter=delimiter)
            col_names = self.new_col_names[1:]

            row_names = []
            values = []
            for row in rdr:

                log2fc_val = row.get('log2_fold_change')
                # print 'FC_VAL: ', log2fc_val
                if '-inf' in str(log2fc_val):
                    row['log2_fold_change'] = -float(max_value)
                elif 'inf' in str(log2fc_val):
                    row['log2_fold_change'] = float(max_value)
                elif 'nan' in str(log2fc_val):
                    row['log2_fold_change'] = None

                try:
                    values.append([float(row[v]) for v in self.new_col_names[1:]])
                except:
                    values.append([None] + [float(row[v]) for v in self.new_col_names[2:]])

                row_names.append(row[self.new_col_names[0]])

        tmatrix = {'row_ids': row_names,
                   'col_ids': col_names,
                   'values': values
                   }

        return tmatrix

    def save_diff_expr_matrix(self, obj_name, data_matrix, condition1, condition2):

        dem_data = {
                    'genome_ref': self.params.get('genome_ref'),
                    'data': data_matrix,
                    'condition_mapping': {condition1: condition2},
                    'type': 'log2_level',
                    'scale': '1.0'
                    }
        res = self.dfu.save_objects({'id': self.params.get('ws_id'),
                                           "objects": [{
                                               "type": "KBaseFeatureValues.DifferentialExpressionMatrix",
                                               "data": dem_data,
                                               "name": obj_name,
                                               "extra_provenance_input_refs": [self.params.get('genome_ref')]
                                           }]
                                           })[0]
        ret_ref = str(res[6]) + '/' + str(res[0]) + '/' + str(res[4])
        return ret_ref

    def save_diff_expr_matrix_set(self, obj_name, matrix_set):

        res = self.setAPI.save_differential_expression_matrix_set_v1({
                                        "workspace": self.params.get('ws_name'),
                                        "output_object_name": obj_name,
                                        "data": matrix_set
                                        })
        return res.get('set_ref')


    # 
    # ballgown always outputs a linear fold change, which we need to convert to log2 
    # before storing
    #

    def safely_apply_log2_to_fc( self, row ):
       if row[0]:                                                                   
           fc = row[0]                                                              
           if fc < 1.0e-10:                                                         
               fc = fc + 1.0e-10   # incase fc is zero                              
           return( [ log2( fc ) ] + row[1:] )                                       
       else:                                                                        
           return( row ) 

    def process_ballgown_file(self, diffexpr_filepath):

        ballgown_col_names = ['id', 'fc', 'pval', 'qval']
        
        data_matrix = self.gen_matrix(diffexpr_filepath,
                                      ballgown_col_names,
                                      delimiter='\t')
        log2_data_matrix = data_matrix
        log2_data_matrix['values'] = map( self.safely_apply_log2_to_fc, data_matrix.get( 'values' ) )

        dem_ref = self.save_diff_expr_matrix(self.params.get('obj_name')+'_0',
                                             log2_data_matrix, None, None)
        set_items = [{
                    'label': 'global Differential Expression Data',
                    'ref': dem_ref
                    }]
        matrix_set = {
                    'description': 'ballgown Diff Exp Matrix Set',
                    'items': set_items
                     }
        return self.save_diff_expr_matrix_set(self.params.get('obj_name'), matrix_set)


    def process_deseq_file(self, diffexpr_filepath):

        deseq_col_names = ['geneID',
                           'log2FoldChange',
                           'pvalue',
                           'padj']

        data_matrix = self.gen_matrix(diffexpr_filepath,
                                      deseq_col_names,
                                      delimiter=',')

        dem_ref = self.save_diff_expr_matrix(self.params.get('obj_name')+'_0',
                                             data_matrix, None, None)
        set_items = [{
                        'label': 'global Differential Expression Data',
                        'ref': dem_ref
                    }]
        matrix_set = {
                        'description': 'deseq Diff Exp Matrix Set',
                        'items': set_items
                     }
        return self.save_diff_expr_matrix_set(self.params.get('obj_name'), matrix_set)

    def process_cuffdiff_file(self, diffexpr_filepath):

        cuffdiff_col_names = ['gene',
                              'log2(fold_change)',
                              'p_value',
                              'q_value']

        ConditionPair = namedtuple("ConditionPair", ["condition1", "condition2"])
        FileInfo = namedtuple('FileInfo', ['file_path', 'file_obj'])

        condPair_fileInfo = {}

        timestamp = str(int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds() * 1000))
        with open(diffexpr_filepath, 'rb') as source:
            rdr = csv.DictReader(source, dialect='excel-tab')
            """
            save the files opened for writing in outfiles list, so they can be closed later
            """
            outfiles = list()

            for r in rdr:
                c1 = r['sample_1']
                c2 = r['sample_2']

                cond_pair = ConditionPair(condition1=c1,
                                          condition2=c2)
                tsv_file_info = condPair_fileInfo.get(cond_pair, None)
                if tsv_file_info is None:
                    tsv_file_name = timestamp + '_' + c1 + '~~' + c2
                    tsv_file_path = os.path.join(self.scratch, tsv_file_name)
                    outfile = open(tsv_file_path, 'wb')
                    outfiles.append(outfile)
                    csv_wtr = csv.DictWriter(outfile, delimiter='\t', fieldnames=self.new_col_names)
                    csv_wtr.writerow(dict((cn, cn) for cn in self.new_col_names))
                    tsv_file_info = FileInfo(file_path=tsv_file_path,
                                             file_obj=csv_wtr)
                    condPair_fileInfo[cond_pair] = tsv_file_info

                wtr = tsv_file_info.file_obj
                col_vals = [r[v] for v in cuffdiff_col_names]
                wtr.writerow(dict(zip(self.new_col_names, col_vals)))

            for ofile in outfiles:
                ofile.close()

            set_items = list()
            for cond_pair, file_info in condPair_fileInfo.iteritems():
                print('Cond_pair: ', cond_pair)
                print('File: ', file_info.file_path)
                tsv_file = file_info.file_path

                data_matrix = self.gen_cuffdiff_matrix(tsv_file)

                object_name = self.get_obj_name(self.params['obj_name'], cond_pair.condition1, cond_pair.condition2)
                dem_ref = self.save_diff_expr_matrix(object_name,
                                                     data_matrix,
                                                     cond_pair.condition1,
                                                     cond_pair.condition2)
                print('process_cuffdiff_file: DEM_REF: ' + dem_ref)
                set_items.append({
                                    'label': cond_pair.condition1+', '+cond_pair.condition2,
                                    'ref': dem_ref
                                    })

        matrix_set = {
                        'description': 'cuffdiff Diff Exp Matrix Set',
                        'items': set_items
                      }
        return self.save_diff_expr_matrix_set(self.params.get('obj_name'), matrix_set)

    """
    Functions for save_differentialExpressionMatrixSet
    """

    def save_matrix(self, genome_ref, infile, in_col_names, delimiter):

        feature_ids = self.get_feature_ids(genome_ref)

        with open(infile, 'rb') as source:
            rdr = csv.DictReader(source, delimiter=delimiter)
            col_names = in_col_names[1:]
            row_names = []
            values = []
            for row in rdr:
                if row[in_col_names[0]] in feature_ids:
                    row_names.append(row[in_col_names[0]])
                else:
                    gene_ids = row[in_col_names[0]].strip().split(',')
                    match = True
                    mismatched_gene_ids = list()
                    for gene_id in gene_ids:
                        gene_id = gene_id.strip()
                        if gene_id not in feature_ids:
                            mismatched_gene_ids.append(gene_id)
                            match = False
                    if match:
                        row_names.append(row[in_col_names[0]])
                    else:
                        error_msg = 'Gene_id(s) "{}" is not a known feature in "{}"'.format(
                            ', '.join(mismatched_gene_ids), self.params.get('genome_ref'))
                        raise ValueError(error_msg)
                try:
                    values.append([float(row[v]) for v in in_col_names[1:]])
                except:
                    values_list = []
                    for v in in_col_names[1:]:
                        tmpval = row[v]
                        if isinstance(tmpval, (int, long, float)):
                            values_list.append(float(tmpval))
                        elif isinstance(tmpval, basestring):
                            if 'na' in tmpval.lower() or 'none' in tmpval.lower():
                                values_list.append(None)
                            else:
                                tmpval = tmpval.replace("'", "")
                                tmpval = tmpval.replace('"', '')
                                values_list.append(float(tmpval))
                        else:
                            raise ValueError("invalid type in input file: {}".format(tmpval))
                    values.append(values_list)

        twoD_matrix = {'row_ids': row_names,
                       'col_ids': col_names,
                       'values': values
                       }

        return twoD_matrix

    @staticmethod
    def get_obj_name(obj_name, condition1, condition2):
        def sanitize(ws_name):
            # I'm not using translate because it's a mess with mixed unicode & strings
            return ws_name.replace("\t", " ").replace(" ", "_").replace("/", "|")

        return "{}-{}-VS-{}".format(obj_name, sanitize(condition2), sanitize(condition1))

    def gen_diffexpr_matrices(self, params):

        print('In GEN DEMs')
        self.params = params
        self.setup_data()
        diffexpr_filepath = self.params.get('diffexpr_filepath')

        if 'deseq' in self.params.get('tool_used').lower():
            dem_ref = self.process_deseq_file(diffexpr_filepath)
        elif 'ballgown' in self.params.get('tool_used').lower():
            dem_ref = self.process_ballgown_file(diffexpr_filepath)
        elif 'cuffdiff' in self.params.get('tool_used').lower():
            dem_ref = self.process_cuffdiff_file(diffexpr_filepath)
        else:
            raise ValueError('"{}" is not a valid tool_used parameter'
                             .format(self.params.get('tool_used')))
        return dem_ref

    def save_diffexpr_matrices(self, params):

        print('In SAVE DEMs')
        self.params = params
        self.setup_data()

        set_items = list()
        for deFile in self.params.get('diffexpr_data'):
            condition_mapping = deFile.get('condition_mapping')
            diffexpr_filepath = deFile.get('diffexpr_filepath')

            if deFile.get('delimter', None) is not None:
                delimiter = deFile.get('delimter')
            else:
                delimiter = '\t'
                fileext = os.path.splitext(diffexpr_filepath)[1]

                if 'csv' in fileext.lower():
                    delimiter = ','
                elif 'tsv' in fileext.lower():
                    delimiter = '\t'
                else:
                    print('Using tab delimiter')

            data_matrix = self.save_matrix(self.params.get('genome_ref'),
                                           diffexpr_filepath,
                                           self.new_col_names,
                                           delimiter)

            condition1, condition2 = condition_mapping.items()[0]
            object_name = self.get_obj_name(self.params['obj_name'], condition1, condition2)
            dem_ref = self.save_diff_expr_matrix(object_name,
                                                 data_matrix,
                                                 condition1,
                                                 condition2 )
            set_items.append({
                'label': condition1 + ', ' + condition2,
                'ref': dem_ref
            })

        matrix_set = {
            'description': self.params.get('tool_used') + ' Differential Expression Matrix Set',
            'items': set_items
        }
        return self.save_diff_expr_matrix_set(self.params.get('obj_name'), matrix_set)




