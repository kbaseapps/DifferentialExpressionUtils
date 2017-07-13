import os
import csv
import uuid
from pprint import pprint
from datetime import datetime
from collections import namedtuple

from Workspace.WorkspaceClient import Workspace as Workspace
from KBaseFeatureValues.KBaseFeatureValuesClient import KBaseFeatureValues

class GenDiffExprMatrix:

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = os.path.join(config['scratch'], 'DEM_' + str(uuid.uuid4()))
        self.ws_url = config['workspace-url']
        self.ws_client = Workspace(self.ws_url)
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

    def setup_data(self):

        self.new_col_names = ['gene_id', 'log2_fold_change', 'p_value', 'q_value']

    def gen_matrix(self, infile, old_col_names, delimiter):
        with open(infile, 'rb') as source:
            rdr = csv.DictReader(source, delimiter=delimiter)
            col_names = self.new_col_names[1:]
            print col_names
            row_names = []
            values = []
            for row in rdr:
                print row
                try:
                    values.append([float(row[v]) for v in old_col_names[1:]])
                    row_names.append(row[old_col_names[0]])
                except:
                    continue

        twoD_matrix = { 'row_ids': row_names,
                        'col_ids': col_names,
                        'values': values
                        }

        return twoD_matrix

    def csv_to_tsv(self, infile, outfile, col_names, delimiter):

        print('OUT FILE: ' + outfile)
        with open(infile, 'rb') as source:
            rdr = csv.DictReader(source, delimiter=delimiter)
            with open(outfile, 'wb') as result:
                wtr = csv.DictWriter(result, delimiter='\t', fieldnames=self.new_col_names)
                wtr.writerow(dict((cn, cn) for cn in self.new_col_names))
                for r in rdr:
                    col_vals = [r[v] for v in col_names]
                    wtr.writerow(dict(zip(self.new_col_names, col_vals)))

    def get_max_fold_change_to_handle_inf(self, infile):
        maxvalue = 0
        with open(infile) as source:
            rdr = csv.DictReader(source, dialect='excel-tab')
            for line in rdr:
                log2fc_val = line.get('log2_fold_change')
                if not 'inf' in str(log2fc_val):
                    log2fc = abs(float(log2fc_val))
                    if (log2fc > maxvalue):
                        maxvalue = log2fc
                        print 'MAX_VAL: ', maxvalue

            print 'maxvalue: ', maxvalue
            return maxvalue

    def replace_inf(self, infile, outfile):

        max_val = self.get_max_fold_change_to_handle_inf(infile)
        with open(infile) as source:
            rdr = csv.DictReader(source, dialect='excel-tab')
            col_names = rdr.fieldnames
            with open(outfile, 'wb') as result:
                wtr = csv.DictWriter(result, delimiter='\t', fieldnames=col_names)
                wtr.writerow(dict((cn, cn) for cn in col_names))

                for line in rdr:
                    # print 'LINE: ', line
                    log2fc_val = line.get('log2_fold_change')
                    if '-inf' in str(log2fc_val):
                        line['log2_fold_change'] = -float(max_val)
                    if 'inf' in str(log2fc_val):
                        line['log2_fold_change'] = max_val

                    wtr.writerow(line)

    def save_diff_expr_matrix(self, obj_name, data_matrix, condition1, condition2):

        dem_data = {
            'data': data_matrix,
            'condition_mapping': {condition1: condition2},
            'type': 'log2_level',
            'scale': '1.0'
        }
        res = self.ws_client.save_objects({'id': self.params.get('ws_id'),
                                           "objects": [{
                                               "type": "KBaseFeatureValues.DifferentialExpressionMatrix",
                                               "data": dem_data,
                                               "name": obj_name
                                           }]
                                           })[0]
        ret_ref = str(res[6]) + '/' + str(res[0]) + '/' + str(res[4])
        return ret_ref

    def save_diff_expr_matrix_set(self, name, data):
        pass

    def process_ballgown_file(self, diffexpr_filepath):

        ballgown_col_names = ['id', 'fc', 'pval', 'qval']

        data_matrix = self.gen_matrix(diffexpr_filepath,
                                      ballgown_col_names,
                                      delimiter='\t')

        dem_ref = self.save_diff_expr_matrix(self.params.get('obj_name'),
                                             data_matrix, None, None)
        print('process_ballgown_file: DEM_REF: ' + dem_ref)
        return dem_ref


    def process_deseq_file(self, diffexpr_filepath):

        deseq_col_names = ['geneID',
                           'log2FoldChange',
                           'pvalue',
                           'padj']

        data_matrix = self.gen_matrix(diffexpr_filepath,
                                      deseq_col_names,
                                      delimiter=',')

        dem_ref = self.save_diff_expr_matrix(self.params.get('obj_name'),
                                             data_matrix, None, None)
        return dem_ref


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
                    csv_wtr = csv.DictWriter(outfile, delimiter='\t', fieldnames=self.new_col_names)
                    csv_wtr.writerow(dict((cn, cn) for cn in self.new_col_names))
                    condPair_fileInfo[cond_pair] = FileInfo(file_path=tsv_file_path,
                                                            file_obj=csv_wtr)
                else:
                    wtr = tsv_file_info.file_obj
                    col_vals = [r[v] for v in cuffdiff_col_names]
                    print 'COL_VALS: ', col_vals
                    wtr.writerow(dict(zip(self.new_col_names, col_vals)))

            count = 0
            dem_ref_list = []
            for cond_pair, file_info in condPair_fileInfo.iteritems():
                print 'Cond_pair: ', cond_pair
                print 'File: ', file_info.file_path
                tsv_file = file_info.file_path
                self.replace_inf(tsv_file, tsv_file+'.tsv')

                data_matrix = self.gen_matrix(diffexpr_filepath,
                                              cuffdiff_col_names,
                                              delimiter='\t')

                dem_ref = self.save_diff_expr_matrix(self.params.get('obj_name')+'_'+str(count),
                                                                     data_matrix,
                                                                     cond_pair.condition1,
                                                                     cond_pair.condition2)
                print('process_cuffdiff_file: DEM_REF: ' + dem_ref)
                dem_ref_list.append(dem_ref)

                count += 1

                print('^^^^^^^^^^^  CUFF  DIFF   ^^^^^^^^^^^^^^^^^')
                print(cond_pair)
                print(dem_ref)
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^')


    def create_diffexpr_matrix(self, tsv_file, condition1, condition2):

        tsv_file_to_DEmatrix_params = { 'input_file_path': expression_matrix_file,
                                        'genome_ref': self.expression_set_data.get('genome_id'),
                                        'data_type': 'log2_level',
                                        'data_scale': '1.0',
                                        'output_ws_name': workspace_name,
                                        'output_obj_name': filtered_expression_matrix_name}
        diffExprMat_ref = fv.tsv_to_DEMatrix(tsv_file_to_DEmatrix_params)['output_matrix_ref']


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
