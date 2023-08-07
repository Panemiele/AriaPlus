package it.uniroma3.bigdata.ariaplus.cityMS.domain;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@JsonPropertyOrder({
        "name", "asciiName", "latitude", "longitude", "country", "iso2",
        "iso3", "adminName", "capital", "population", "id"
})
public class City {
    private String name;
    private String asciiName;
    private float latitude;
    private float longitude;
    private String country;
    private String iso2;
    private String iso3;
    private String adminName;
    private String capital;
    private Integer population;
    private String id;
}
