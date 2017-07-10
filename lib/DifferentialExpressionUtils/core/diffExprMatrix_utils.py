import os
import csv
import uuid
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

        self.deseq_change_cols = {'geneID': 'gene_id',
                                  'log2FoldChange': 'log2_fold_change',
                                  'pvalue': 'p_value',
                                  'padj': 'q_value'}

        self.ballgown_change_cols = {'id': 'gene_id',
                                     'fc': 'log2_fold_change',
                                     'pval': 'p_value',
                                     'qval': 'q_value'}

        self.cuffdiff_change_cols = {'log2(fold_change)': 'log2_fold_change'}

    def csv_to_tsv(self, infile, outfile, col_names_dict, delimiter=','):
        with open(infile, 'rb') as source:
            rdr = csv.reader(source, delimiter=delimiter)
            with open(outfile, 'wb') as result:
                col_names = next(rdr)
                for cindex, cval in enumerate(col_names):
                    print 'col name: ' + cval
                    for oldcol, newcol in col_names_dict.iteritems():
                        if oldcol in cval:
                            col_names[cindex] = cval.replace(oldcol, newcol)
                            print 'new name: ' + newcol
                
                result.write('\t'.join(col_names) + '\n')

                for r in rdr:
                    result.write('\t'.join(r) + '\n')

    def process_ballgown_file(self, diffexpr_filepath):
        timestamp = str(int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds() * 1000))
        diffexpr_tsv_file = os.path.join(self.scratch, timestamp + '_ballgown_diffexp.tsv')

        self.csv_to_tsv(diffexpr_filepath,
                        diffexpr_tsv_file,
                        self.ballgown_change_cols,
                        delimiter='\t')

        tsv_file_to_matrix_params = {'input_file_path': diffexpr_tsv_file,
                                     'genome_ref': self.params.get('genome_ref'),
                                     'data_type': 'log2_level',
                                     'data_scale': '1.0',
                                     'output_ws_name': self.params.get('ws_name'),
                                     'output_obj_name': self.params.get('obj_name') + '_DEM'
                                     }
        matrix_ref = self.fv.tsv_file_to_matrix(tsv_file_to_matrix_params)['output_matrix_ref']
        return matrix_ref

    def process_deseq_file(self, diffexpr_filepath):

        timestamp = str(int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds() * 1000))
        diffexpr_tsv_file = os.path.join(self.scratch, timestamp + '_deseq_diffexp.tsv')

        self.csv_to_tsv(diffexpr_filepath,
                        diffexpr_tsv_file,
                        self.deseq_change_cols)

        tsv_file_to_matrix_params = {'input_file_path': diffexpr_tsv_file,
                                     'genome_ref': self.params.get('genome_ref'),
                                     'data_type': 'log2_level',
                                     'data_scale': '1.0',
                                     'output_ws_name': self.params.get('ws_name'),
                                     'output_obj_name': self.params.get('obj_name')
                                     }

        matrix_ref = self.fv.tsv_file_to_matrix(tsv_file_to_matrix_params)['output_matrix_ref']
        return matrix_ref

    def process_cuffdiff_file(self, diffexpr_filepath):

        ConditionPair = namedtuple("ConditionPair", ["condition1", "condition2"])
        FileInfo = namedtuple('FileInfo', ['file_path', 'file_obj'])

        condPair_fileInfo = {}

        timestamp = str(int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds() * 1000))
        with open(diffexpr_filepath, 'rb') as source:
            rdr = csv.DictReader(source, dialect='excel-tab')
            col_names = rdr.fieldnames
            print 'OLD_col_names: ', col_names
            for cindex, cval in enumerate(col_names):
                for oldcol, newcol in self.cuffdiff_change_cols.iteritems():
                    if oldcol in cval:
                        col_names[cindex] = cval.replace(oldcol, newcol)
                        print 'new name: ' + newcol
            print 'NEW_col_names: ', col_names

            for r in rdr:
                c1 = r['sample_1']
                c2 = r['sample_2']

                cond_pair = ConditionPair(condition1=c1,
                                          condition2=c2)
                tsv_file_info = condPair_fileInfo.get(cond_pair, None)
                if tsv_file_info is None:
                    tsv_file_name = timestamp + '_' + c1 + '_' + c2 + '.tsv'
                    tsv_file_path = os.path.join(self.scratch, tsv_file_name)
                    outfile = open(tsv_file_path, 'wb')
                    csv_wtr = csv.DictWriter(outfile, delimiter='\t', fieldnames=col_names)
                    csv_wtr.writerow(dict((cn, cn) for cn in col_names))
                    condPair_fileInfo[cond_pair] = FileInfo(file_path=tsv_file_path,
                                                            file_obj=csv_wtr)
                else:
                    wtr = tsv_file_info.file_obj
                    wtr.writerow(r)

            count = 0
            for cond_pair, file_info in condPair_fileInfo.iteritems():
                print 'Cond_pair: ', cond_pair
                print 'File: ', file_info.file_path
                condition_mapping = {cond_pair.condition1: cond_pair.condition2}
                tsv_file = file_info.file_path
                tsv_file_to_DEmatrix_params = {'input_file_path': tsv_file,
                                               'genome_ref': self.params.get('genome_ref'),
                                               'data_type': 'log2_level',
                                               'data_scale': '1.0',
                                               'output_ws_name': self.params.get('ws_name'),
                                               'output_obj_name': self.params.get('obj_name')
                                                                  + 'DEM_' + str(count)}
                count += 1
                matrix_ref = self.fv.tsv_file_to_matrix(tsv_file_to_DEmatrix_params)['output_matrix_ref']

                print('^^^^^^^^^^^  CUFF  DIFF   ^^^^^^^^^^^^^^^^^')
                print(cond_pair)
                print(matrix_ref)
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
        diffexpr_filepath = os.path.join(self.params.get('source_dir'),
                                         self.params.get('diffexpr_filename'))

        if 'deseq' in self.params.get('tool_used').lower():
            self.process_deseq_file(diffexpr_filepath)
        elif 'ballgown' in self.params.get('tool_used').lower():
            self.process_ballgown_file(diffexpr_filepath)
        elif 'cuffdiff' in self.params.get('tool_used').lower():
            self.process_cuffdiff_file(diffexpr_filepath)
        else:
            raise ValueError('"{}" is not a valid tool_used parameter'
                             .format(self.params.get('tool_used')))
