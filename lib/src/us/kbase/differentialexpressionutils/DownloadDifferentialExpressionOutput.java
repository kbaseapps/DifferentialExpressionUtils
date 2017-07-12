
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
 * <p>Original spec-file type: DownloadDifferentialExpressionOutput</p>
 * <pre>
 * *  The output of the download method.  *
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "destination_dir"
})
public class DownloadDifferentialExpressionOutput {

    @JsonProperty("destination_dir")
    private String destinationDir;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("destination_dir")
    public String getDestinationDir() {
        return destinationDir;
    }

    @JsonProperty("destination_dir")
    public void setDestinationDir(String destinationDir) {
        this.destinationDir = destinationDir;
    }

    public DownloadDifferentialExpressionOutput withDestinationDir(String destinationDir) {
        this.destinationDir = destinationDir;
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
        return ((((("DownloadDifferentialExpressionOutput"+" [destinationDir=")+ destinationDir)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
