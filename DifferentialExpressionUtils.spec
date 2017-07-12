/*
A KBase module: DifferentialExpressionUtils
*/

module DifferentialExpressionUtils {

/**
    A KBase module: DifferentialExpressionUtils

    This module uploads, downloads and exports DifferentialExpression and ExpressionMatrix objects
**/

   /* A boolean - 0 for false, 1 for true.
       @range (0, 1)
   */

    typedef int boolean;

   /**    Required input parameters for uploading Differential expression data

        string   destination_ref        -   object reference of Differential expression data.
                                            The object ref is 'ws_name_or_id/obj_name_or_id'
                                            where ws_name_or_id is the workspace name or id
                                            and obj_name_or_id is the object name or id
        string   source_dir             -   directory with the files to be uploaded
        string   expressionset_ref      -   expressionset object reference
        string   tool_used              -   cufflinks, ballgown or deseq
        string   tool_version           -   version of the tool used
        string   diffexpr_filename      -   name of the differential expression data file
                                            in source_dir, created by cuffdiff, deseq or ballgown
    **/

    typedef structure {

        string   destination_ref;
        string   source_dir;
        string   expressionset_ref;
        string   tool_used;
        string   tool_version;
        string   diffexpr_filename;

        mapping<string opt_name, string opt_value> tool_opts;   /* Optional */
        string   comments;                                      /* Optional */

    }  UploadDifferentialExpressionParams;


    /**     Output from upload differential expression    **/

    typedef structure {
        string   obj_ref;
     }  UploadDifferentialExpressionOutput;

    /**  Uploads the differential expression  **/

    funcdef  upload_differentialExpression(UploadDifferentialExpressionParams params)
                                   returns (UploadDifferentialExpressionOutput)
                                   authentication required;
    /**
        Required input parameters for downloading Differential expression
        string  source_ref   -      object reference of expression source. The
                                    object ref is 'ws_name_or_id/obj_name_or_id'
                                    where ws_name_or_id is the workspace name or id
                                    and obj_name_or_id is the object name or id
    **/


    typedef structure {
        string      source_ref;
    } DownloadDifferentialExpressionParams;

    /**  The output of the download method.  **/

    typedef structure {
        string    destination_dir;      /* directory containing all the downloaded files  */
    } DownloadDifferentialExpressionOutput;

    /** Downloads expression **/

    funcdef download_differentialExpression(DownloadDifferentialExpressionParams params)
                       returns (DownloadDifferentialExpressionOutput)
                       authentication required;

    /**
        Required input parameters for exporting expression

        string   source_ref 	-   object reference of Differential expression. The
                                    object ref is 'ws_name_or_id/obj_name_or_id'
                                    where ws_name_or_id is the workspace name or id
                                    and obj_name_or_id is the object name or id
     **/

    typedef structure {
        string source_ref;   /* workspace object reference */
    } ExportParams;

    typedef structure {
        string shock_id;     /* shock id of file to export */
     } ExportOutput;
    /** Wrapper function for use by in-narrative downloaders to download expressions from shock **/


    funcdef export_differentialExpression(ExportParams params)
                     returns (ExportOutput output)
                     authentication required;
};
