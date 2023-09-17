package it.uniroma3.bigdata.ariaplus.cityMS.api.controller.impl;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import it.uniroma3.bigdata.ariaplus.cityMS.api.controller.CityIngestionController;
import it.uniroma3.bigdata.ariaplus.cityMS.service.CityIngestionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Tag(name = "CityIngestionController", description = "Defines methods for cities' data ingestion")
@Schema(name = "CityIngestionController", description = "Defines methods for cities' data ingestion")
public class CityIngestionControllerImpl implements CityIngestionController {

    @Autowired
    public CityIngestionService cityIngestionService;

    @Override
    @Operation(description = "Retrieve cities' data from the \"worldcities.csv\" file and send them to the Kafka topic.",
            responses = {
                    @ApiResponse(
                            responseCode = "200", description = "Cities' data sent to topic succesfully"
                    ),
                    @ApiResponse(
                            responseCode = "400", description = "There's something wrong in the request. Please, try again."
                    ),
                    @ApiResponse(
                            responseCode = "404", description = "No file \"worldcities.csv\" file has been found."
                    )
            }
    )
    public void sendCitiesInfosToTopic() {
        cityIngestionService.sendCitiesInfosToTopic();
    }
}
