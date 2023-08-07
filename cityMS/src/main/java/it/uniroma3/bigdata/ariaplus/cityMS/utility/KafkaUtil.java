package it.uniroma3.bigdata.ariaplus.cityMS.utility;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import it.uniroma3.bigdata.ariaplus.cityMS.domain.City;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

import java.util.List;
import java.util.Properties;

public class KafkaUtil {

    private static final ObjectMapper mapper = new ObjectMapper();

    public static KafkaProducer<String, String> createProducer(String host, String port) {
        Properties properties = new Properties();
        properties.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, host + ":" + port);
        properties.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        properties.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        return new KafkaProducer<>(properties);
    }

    public static void sendCitiesToTopic(String host, String port, String topic, List<City> citiesList) {
        KafkaProducer<String, String> producer = createProducer(host, port);

        citiesList.forEach(city -> {
            try {
                producer.send(new ProducerRecord<>(topic, mapper.writeValueAsString(city)));
            } catch (JsonProcessingException e) {
                e.printStackTrace();
            }
        });
        producer.close();
    }
}
