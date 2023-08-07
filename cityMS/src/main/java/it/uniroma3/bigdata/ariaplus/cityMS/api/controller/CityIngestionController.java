package it.uniroma3.bigdata.ariaplus.cityMS.api.controller;

import org.springframework.web.bind.annotation.PostMapping;


public interface CityIngestionController {

    @PostMapping("/send-cities")
    public void sendCitiesInfosToTopic();
}
