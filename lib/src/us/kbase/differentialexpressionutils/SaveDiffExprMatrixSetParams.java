
package us.kbase.differentialexpressionutils;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: SaveDiffExprMatrixSetParams</p>
 * <pre>
 * *    Required input parameters for saving Differential expression data
 *         string   destination_ref         -  object reference of Differential expression data.
 *                                             The object ref is 'ws_name_or_id/obj_name_or_id'
 *                                             where ws_name_or_id is the workspace name or id
 *                                             and obj_name_or_id is the object name or id
 *         list<DiffExprFile> diffexpr_data -  list of DiffExprFiles (condition pair & file)
 *         string   tool_used               -  cufflinks, ballgown or deseq
 *         string   tool_version            -  version of the tool used
 *         string   genome_ref              -  genome object reference
 *     *
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "destination_ref",
    "diffexpr_data",
    "tool_used",
    "tool_version",
    "genome_ref",
    "description",
    "type",
    "scale"
})
public class SaveDiffExprMatrixSetParams {

    @JsonProperty("destination_ref")
    private String destinationRef;
    @JsonProperty("diffexpr_data")
    private List<DiffExprFile> diffexprData;
    @JsonProperty("tool_used")
    private String toolUsed;
    @JsonProperty("tool_version")
    private String toolVersion;
    @JsonProperty("genome_ref")
    private String genomeRef;
    @JsonProperty("description")
    private String description;
    @JsonProperty("type")
    private String type;
    @JsonProperty("scale")
    private String scale;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("destination_ref")
    public String getDestinationRef() {
        return destinationRef;
    }

    @JsonProperty("destination_ref")
    public void setDestinationRef(String destinationRef) {
        this.destinationRef = destinationRef;
    }

    public SaveDiffExprMatrixSetParams withDestinationRef(String destinationRef) {
        this.destinationRef = destinationRef;
        return this;
    }

    @JsonProperty("diffexpr_data")
    public List<DiffExprFile> getDiffexprData() {
        return diffexprData;
    }

    @JsonProperty("diffexpr_data")
    public void setDiffexprData(List<DiffExprFile> diffexprData) {
        this.diffexprData = diffexprData;
    }

    public SaveDiffExprMatrixSetParams withDiffexprData(List<DiffExprFile> diffexprData) {
        this.diffexprData = diffexprData;
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

    public SaveDiffExprMatrixSetParams withToolUsed(String toolUsed) {
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

    public SaveDiffExprMatrixSetParams withToolVersion(String toolVersion) {
        this.toolVersion = toolVersion;
        return this;
    }

    @JsonProperty("genome_ref")
    public String getGenomeRef() {
        return genomeRef;
    }

    @JsonProperty("genome_ref")
    public void setGenomeRef(String genomeRef) {
        this.genomeRef = genomeRef;
    }

    public SaveDiffExprMatrixSetParams withGenomeRef(String genomeRef) {
        this.genomeRef = genomeRef;
        return this;
    }

    @JsonProperty("description")
    public String getDescription() {
        return description;
    }

    @JsonProperty("description")
    public void setDescription(String description) {
        this.description = description;
    }

    public SaveDiffExprMatrixSetParams withDescription(String description) {
        this.description = description;
        return this;
    }

    @JsonProperty("type")
    public String getType() {
        return type;
    }

    @JsonProperty("type")
    public void setType(String type) {
        this.type = type;
    }

    public SaveDiffExprMatrixSetParams withType(String type) {
        this.type = type;
        return this;
    }

    @JsonProperty("scale")
    public String getScale() {
        return scale;
    }

    @JsonProperty("scale")
    public void setScale(String scale) {
        this.scale = scale;
    }

    public SaveDiffExprMatrixSetParams withScale(String scale) {
        this.scale = scale;
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
        return ((((((((((((((((((("SaveDiffExprMatrixSetParams"+" [destinationRef=")+ destinationRef)+", diffexprData=")+ diffexprData)+", toolUsed=")+ toolUsed)+", toolVersion=")+ toolVersion)+", genomeRef=")+ genomeRef)+", description=")+ description)+", type=")+ type)+", scale=")+ scale)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
