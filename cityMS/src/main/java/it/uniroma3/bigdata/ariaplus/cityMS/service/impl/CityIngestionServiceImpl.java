package it.uniroma3.bigdata.ariaplus.cityMS.service.impl;

import it.uniroma3.bigdata.ariaplus.cityMS.domain.City;
import it.uniroma3.bigdata.ariaplus.cityMS.service.CityIngestionService;
import it.uniroma3.bigdata.ariaplus.cityMS.utility.CsvFileReaderUtil;
import it.uniroma3.bigdata.ariaplus.cityMS.utility.KafkaUtil;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;

@Service
public class CityIngestionServiceImpl implements CityIngestionService {

    @Value("${kafka.host}")
    private String kafkaHost;
    @Value("${kafka.port}")
    private String kafkaPort;
    @Value("${kafka.topic}")
    private String kafkaTopic;

    @Override
    public void sendCitiesInfosToTopic() {
        try {
            Resource resource = new ClassPathResource("cityDataset/worldcities.csv");
            BufferedReader reader = new BufferedReader(new InputStreamReader(resource.getInputStream()));
            List<City> citiesList = CsvFileReaderUtil.loadCsvContentToList(reader);
            KafkaUtil.sendCitiesToTopic(kafkaHost, kafkaPort, kafkaTopic, citiesList);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
