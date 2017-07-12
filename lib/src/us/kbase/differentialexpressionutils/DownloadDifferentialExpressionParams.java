
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
 * <p>Original spec-file type: DownloadDifferentialExpressionParams</p>
 * <pre>
 * *
 * Required input parameters for downloading Differential expression
 * string  source_ref   -      object reference of expression source. The
 *                             object ref is 'ws_name_or_id/obj_name_or_id'
 *                             where ws_name_or_id is the workspace name or id
 *                             and obj_name_or_id is the object name or id
 *     *
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "source_ref"
})
public class DownloadDifferentialExpressionParams {

    @JsonProperty("source_ref")
    private String sourceRef;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("source_ref")
    public String getSourceRef() {
        return sourceRef;
    }

    @JsonProperty("source_ref")
    public void setSourceRef(String sourceRef) {
        this.sourceRef = sourceRef;
    }

    public DownloadDifferentialExpressionParams withSourceRef(String sourceRef) {
        this.sourceRef = sourceRef;
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
        return ((((("DownloadDifferentialExpressionParams"+" [sourceRef=")+ sourceRef)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
