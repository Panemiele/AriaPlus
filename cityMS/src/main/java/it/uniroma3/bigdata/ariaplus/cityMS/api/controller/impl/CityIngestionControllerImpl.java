package it.uniroma3.bigdata.ariaplus.cityMS.api.controller.impl;

import it.uniroma3.bigdata.ariaplus.cityMS.api.controller.CityIngestionController;
import it.uniroma3.bigdata.ariaplus.cityMS.service.CityIngestionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;

@Controller
public class CityIngestionControllerImpl implements CityIngestionController {

    @Autowired
    public CityIngestionService cityIngestionService;

    @Override
    public void sendCitiesInfosToTopic() {
        cityIngestionService.sendCitiesInfosToTopic();
    }
}
