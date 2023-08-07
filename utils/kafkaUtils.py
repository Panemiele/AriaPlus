#!/usr/bin/python

import json
from kafka import KafkaProducer, KafkaConsumer

from utils.sparkUtils import publishInKafkaViaSparkStreaming, getKafkaSubscriberDF


#####################
# Functions section #
#####################

# -----------FUNCTIONS FOR STATIC MESSAGES-----------#
def publish_message(producer_instance, topic_name, json):
    try:
        producer_instance.send(topic_name, json)
        print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))


def consume_messages(consumer):
    while True:
        try:
            records = consumer.poll(timeout_ms=1000)
            for topic_data, consumer_records in records.items():
                for consumer_record in consumer_records:
                    print("Received message: " + str(consumer_record.value))
            continue
        except Exception as e:
            print(e)
            continue


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


def connect_kafka_consumer(host_port, topic_name):
    _consumer = None
    try:
        _consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=host_port,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=None,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _consumer


# -----------FUNCTIONS FOR STREAMING MESSAGES-----------#
def publishInKafkaStreaming(app_name, input, host_port, topic_name):
    publishInKafkaViaSparkStreaming(app_name, input, host_port, topic_name)


def subscribeToKafkaStreamingTopic(app_name, host_port, topic_name):
    getKafkaSubscriberDF(app_name, host_port, topic_name)
