
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
 * <p>Original spec-file type: DiffExprFile</p>
 * <pre>
 * ---------------------------------------------------------------------------------
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "condition_mapping",
    "diffexpr_filepath",
    "delimiter"
})
public class DiffExprFile {

    @JsonProperty("condition_mapping")
    private Map<String, String> conditionMapping;
    @JsonProperty("diffexpr_filepath")
    private java.lang.String diffexprFilepath;
    @JsonProperty("delimiter")
    private java.lang.String delimiter;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("condition_mapping")
    public Map<String, String> getConditionMapping() {
        return conditionMapping;
    }

    @JsonProperty("condition_mapping")
    public void setConditionMapping(Map<String, String> conditionMapping) {
        this.conditionMapping = conditionMapping;
    }

    public DiffExprFile withConditionMapping(Map<String, String> conditionMapping) {
        this.conditionMapping = conditionMapping;
        return this;
    }

    @JsonProperty("diffexpr_filepath")
    public java.lang.String getDiffexprFilepath() {
        return diffexprFilepath;
    }

    @JsonProperty("diffexpr_filepath")
    public void setDiffexprFilepath(java.lang.String diffexprFilepath) {
        this.diffexprFilepath = diffexprFilepath;
    }

    public DiffExprFile withDiffexprFilepath(java.lang.String diffexprFilepath) {
        this.diffexprFilepath = diffexprFilepath;
        return this;
    }

    @JsonProperty("delimiter")
    public java.lang.String getDelimiter() {
        return delimiter;
    }

    @JsonProperty("delimiter")
    public void setDelimiter(java.lang.String delimiter) {
        this.delimiter = delimiter;
    }

    public DiffExprFile withDelimiter(java.lang.String delimiter) {
        this.delimiter = delimiter;
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
        return ((((((((("DiffExprFile"+" [conditionMapping=")+ conditionMapping)+", diffexprFilepath=")+ diffexprFilepath)+", delimiter=")+ delimiter)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
