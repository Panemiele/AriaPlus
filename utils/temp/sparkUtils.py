#!/usr/bin/python

from pyspark.sql import SparkSession


def startSparkSession(appName):
    return SparkSession \
        .builder \
        .appName(appName) \
        .getOrCreate()


def getJsonConsumerDF(app_name, json_input):
    try:
        spark = SparkSession \
            .builder \
            .appName(app_name) \
            .getOrCreate()
        df = spark.read.json(json_input).cache()
        return df
    except Exception as e:
        print(e)


def getKafkaSubscriberDF(appName, host_port, topic_name):
    try:
        return startSparkSession(appName) \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", host_port) \
            .option("subscribe", topic_name) \
            .load()
    except Exception as e:
        print(e)


def publishInKafkaViaSparkStreaming(app_name, input, host_port, topic_name):
    try:
        df = getJsonConsumerDF(app_name, input)
        query = df.outputMode("complete") \
            .format("kafka") \
            .option("kafka.bootstrap.servers", host_port) \
            .option("topic", topic_name) \
            .start()
        query.awaitTermination()
    except Exception as e:
        print(e)
