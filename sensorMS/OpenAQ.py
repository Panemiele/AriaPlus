#!/usr/bin/python
import json
import requests
import schedule
import time
from kafka import KafkaProducer

# Instantiate the kafka producer
kafka_host_port = "localhost:9092"
topic_name = "aq-api-ingestion-topic"
base_url = 'https://api.openaq.org/v2/latest'


#####################
# Functions section #
#####################

def connect_kafka_producer(host_port):
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=[host_port],
                                  value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _producer


def get_air_quality():
    parameters = {
        # 'country': airQualityProps['parameters']['country'],
        # 'limit': 4000
    }
    response = requests.get(base_url, params=parameters)
    if response.status_code == 200:
        try:
            for data in response.json()['results']:
                producer.send(topic_name, data)
            print('Messages published successfully.')
        except Exception as ex:
            print('Exception in publishing message')
            print(str(ex))
    else:
        print("Error occurred while fetching data.")


# --------------------------------------------------------------------------------------------------#
producer = connect_kafka_producer(kafka_host_port)

# Schedule the get_air_quality method to run every 30 minutes
schedule.every(30).minutes.do(get_air_quality)
get_air_quality()
while True:
    schedule.run_pending()
    time.sleep(1)
