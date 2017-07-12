
package us.kbase.differentialexpressionutils;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: UploadDifferentialExpressionParams</p>
 * <pre>
 * *    Required input parameters for uploading Differential expression data
 *         string   destination_ref        -   object reference of Differential expression data.
 *                                             The object ref is 'ws_name_or_id/obj_name_or_id'
 *                                             where ws_name_or_id is the workspace name or id
 *                                             and obj_name_or_id is the object name or id
 *         string   source_dir             -   directory with the files to be uploaded
 *         string   expressionset_ref      -   expressionset object reference
 *         string   tool_used              -   cufflinks, ballgown or deseq
 *         string   tool_version           -   version of the tool used
 *         string   diffexpr_filename      -   name of the differential expression data file
 *                                             in source_dir, created by cuffdiff, deseq or ballgown
 *     *
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "destination_ref",
    "source_dir",
    "expressionset_ref",
    "tool_used",
    "tool_version",
    "diffexpr_filename",
    "tool_opts",
    "comments"
})
public class UploadDifferentialExpressionParams {

    @JsonProperty("destination_ref")
    private java.lang.String destinationRef;
    @JsonProperty("source_dir")
    private java.lang.String sourceDir;
    @JsonProperty("expressionset_ref")
    private java.lang.String expressionsetRef;
    @JsonProperty("tool_used")
    private java.lang.String toolUsed;
    @JsonProperty("tool_version")
    private java.lang.String toolVersion;
    @JsonProperty("diffexpr_filename")
    private java.lang.String diffexprFilename;
    @JsonProperty("tool_opts")
    private Map<String, String> toolOpts;
    @JsonProperty("comments")
    private java.lang.String comments;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("destination_ref")
    public java.lang.String getDestinationRef() {
        return destinationRef;
    }

    @JsonProperty("destination_ref")
    public void setDestinationRef(java.lang.String destinationRef) {
        this.destinationRef = destinationRef;
    }

    public UploadDifferentialExpressionParams withDestinationRef(java.lang.String destinationRef) {
        this.destinationRef = destinationRef;
        return this;
    }

    @JsonProperty("source_dir")
    public java.lang.String getSourceDir() {
        return sourceDir;
    }

    @JsonProperty("source_dir")
    public void setSourceDir(java.lang.String sourceDir) {
        this.sourceDir = sourceDir;
    }

    public UploadDifferentialExpressionParams withSourceDir(java.lang.String sourceDir) {
        this.sourceDir = sourceDir;
        return this;
    }

    @JsonProperty("expressionset_ref")
    public java.lang.String getExpressionsetRef() {
        return expressionsetRef;
    }

    @JsonProperty("expressionset_ref")
    public void setExpressionsetRef(java.lang.String expressionsetRef) {
        this.expressionsetRef = expressionsetRef;
    }

    public UploadDifferentialExpressionParams withExpressionsetRef(java.lang.String expressionsetRef) {
        this.expressionsetRef = expressionsetRef;
        return this;
    }

    @JsonProperty("tool_used")
    public java.lang.String getToolUsed() {
        return toolUsed;
    }

    @JsonProperty("tool_used")
    public void setToolUsed(java.lang.String toolUsed) {
        this.toolUsed = toolUsed;
    }

    public UploadDifferentialExpressionParams withToolUsed(java.lang.String toolUsed) {
        this.toolUsed = toolUsed;
        return this;
    }

    @JsonProperty("tool_version")
    public java.lang.String getToolVersion() {
        return toolVersion;
    }

    @JsonProperty("tool_version")
    public void setToolVersion(java.lang.String toolVersion) {
        this.toolVersion = toolVersion;
    }

    public UploadDifferentialExpressionParams withToolVersion(java.lang.String toolVersion) {
        this.toolVersion = toolVersion;
        return this;
    }

    @JsonProperty("diffexpr_filename")
    public java.lang.String getDiffexprFilename() {
        return diffexprFilename;
    }

    @JsonProperty("diffexpr_filename")
    public void setDiffexprFilename(java.lang.String diffexprFilename) {
        this.diffexprFilename = diffexprFilename;
    }

    public UploadDifferentialExpressionParams withDiffexprFilename(java.lang.String diffexprFilename) {
        this.diffexprFilename = diffexprFilename;
        return this;
    }

    @JsonProperty("tool_opts")
    public Map<String, String> getToolOpts() {
        return toolOpts;
    }

    @JsonProperty("tool_opts")
    public void setToolOpts(Map<String, String> toolOpts) {
        this.toolOpts = toolOpts;
    }

    public UploadDifferentialExpressionParams withToolOpts(Map<String, String> toolOpts) {
        this.toolOpts = toolOpts;
        return this;
    }

    @JsonProperty("comments")
    public java.lang.String getComments() {
        return comments;
    }

    @JsonProperty("comments")
    public void setComments(java.lang.String comments) {
        this.comments = comments;
    }

    public UploadDifferentialExpressionParams withComments(java.lang.String comments) {
        this.comments = comments;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((((((((((((("UploadDifferentialExpressionParams"+" [destinationRef=")+ destinationRef)+", sourceDir=")+ sourceDir)+", expressionsetRef=")+ expressionsetRef)+", toolUsed=")+ toolUsed)+", toolVersion=")+ toolVersion)+", diffexprFilename=")+ diffexprFilename)+", toolOpts=")+ toolOpts)+", comments=")+ comments)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
