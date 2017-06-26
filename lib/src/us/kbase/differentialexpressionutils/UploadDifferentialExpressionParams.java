
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
 *         string   expressionSet_ref      -   expressionSet object reference
 *         string   tool_used              -   cufflinks, ballgown or deseq
 *         string   tool_version           -   version of the tool used
 *     *
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "destination_ref",
    "source_dir",
    "expressionSet_ref",
    "tool_used",
    "tool_version"
})
public class UploadDifferentialExpressionParams {

    @JsonProperty("destination_ref")
    private String destinationRef;
    @JsonProperty("source_dir")
    private String sourceDir;
    @JsonProperty("expressionSet_ref")
    private String expressionSetRef;
    @JsonProperty("tool_used")
    private String toolUsed;
    @JsonProperty("tool_version")
    private String toolVersion;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("destination_ref")
    public String getDestinationRef() {
        return destinationRef;
    }

    @JsonProperty("destination_ref")
    public void setDestinationRef(String destinationRef) {
        this.destinationRef = destinationRef;
    }

    public UploadDifferentialExpressionParams withDestinationRef(String destinationRef) {
        this.destinationRef = destinationRef;
        return this;
    }

    @JsonProperty("source_dir")
    public String getSourceDir() {
        return sourceDir;
    }

    @JsonProperty("source_dir")
    public void setSourceDir(String sourceDir) {
        this.sourceDir = sourceDir;
    }

    public UploadDifferentialExpressionParams withSourceDir(String sourceDir) {
        this.sourceDir = sourceDir;
        return this;
    }

    @JsonProperty("expressionSet_ref")
    public String getExpressionSetRef() {
        return expressionSetRef;
    }

    @JsonProperty("expressionSet_ref")
    public void setExpressionSetRef(String expressionSetRef) {
        this.expressionSetRef = expressionSetRef;
    }

    public UploadDifferentialExpressionParams withExpressionSetRef(String expressionSetRef) {
        this.expressionSetRef = expressionSetRef;
        return this;
    }

    @JsonProperty("tool_used")
    public String getToolUsed() {
        return toolUsed;
    }

    @JsonProperty("tool_used")
    public void setToolUsed(String toolUsed) {
        this.toolUsed = toolUsed;
    }

    public UploadDifferentialExpressionParams withToolUsed(String toolUsed) {
        this.toolUsed = toolUsed;
        return this;
    }

    @JsonProperty("tool_version")
    public String getToolVersion() {
        return toolVersion;
    }

    @JsonProperty("tool_version")
    public void setToolVersion(String toolVersion) {
        this.toolVersion = toolVersion;
    }

    public UploadDifferentialExpressionParams withToolVersion(String toolVersion) {
        this.toolVersion = toolVersion;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((((("UploadDifferentialExpressionParams"+" [destinationRef=")+ destinationRef)+", sourceDir=")+ sourceDir)+", expressionSetRef=")+ expressionSetRef)+", toolUsed=")+ toolUsed)+", toolVersion=")+ toolVersion)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
