import requests
import traceback
from decouple import config
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf, explode
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, DoubleType


#####################
# Functions section #
#####################

def writeStreamingInHdfs(data_frame):
    return data_frame \
        .format("json") \
        .trigger(processingTime="10 seconds") \
        .option("url", hdfs_url) \
        .option("path", hdfs_data_path) \
        .option("checkpointLocation", hdfs_checkpoint_location) \
        .start()


def writeStreamingAQCityInfoInNeo4j(data_frame):
    return data_frame \
        .format(neo4j_format) \
        .option("url", neo4j_url) \
        .option("save.mode", neo4j_save_mode) \
        .option("checkpointLocation", neo4j_checkpoint_location) \
        .option("authentication.basic.username", config("neo4j_username")) \
        .option("authentication.basic.password", config("neo4j_password")) \
        .option("labels", "AQCityInfo") \
        .option("node.keys", "city") \
        .start()


def writeStreamingMeasurementInNeo4j(data_frame):
    return data_frame \
        .format(neo4j_format) \
        .option("url", neo4j_url) \
        .option("save.mode", neo4j_save_mode) \
        .option("checkpointLocation", neo4j_checkpoint_location) \
        .option("authentication.basic.username", config("neo4j_username")) \
        .option("authentication.basic.password", config("neo4j_password")) \
        .option("labels", "Measurement") \
        .option("node.keys", "parameter,city") \
        .start()


# Used to debug data frame
def writeInConsole(data_frame):
    return data_frame.format("console").option("truncate", "false").start()


def writeStreamingRelationshipsInNeo4j(data_frame):
    cypher_query = """
        MATCH (aq:AQCityInfo), (m:Measurement)
        WHERE aq.city = m.city
        CREATE (m)-[:IS_MEASUREMENT_OF]->(aq)
    """

    return data_frame \
        .format(neo4j_format) \
        .option("url", neo4j_url) \
        .option("save.mode", neo4j_save_mode) \
        .option("checkpointLocation", neo4j_checkpoint_location) \
        .option("authentication.basic.username", config("neo4j_username")) \
        .option("authentication.basic.password", config("neo4j_password")) \
        .option("query", cypher_query) \
        .start()


def startSparkSession(app_name):
    return SparkSession \
        .builder \
        .appName(app_name) \
        .getOrCreate()


def subscribeToKafkaStreamingTopic(host_port, topic_name):
    try:
        return spark_session \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", host_port) \
            .option("subscribe", topic_name) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
    except Exception as e:
        print(e)


def findCityByCoordinates(latitude, longitude):
    parameters = {
        'format': 'json',
        'lat': str(latitude),
        'lon': str(longitude)
    }
    try:
        response = requests.get(openstreetmap_url_basepath, params=parameters)
        if response.headers["content-type"].strip().startswith("application/json"):
            address = response.json()['address']
            if 'city' in address:
                return address['city']
            elif 'town' in address:
                return address['town']
            else:
                return '---'
        else:
            return '---'
    except Exception as ex:
        print('Exception in retrieving city' + str(ex))
        print(traceback.format_exc())


#####################
# VARIABLES SECTION #
#####################
app_name = "ingestion-util"
kafka_host_port = "localhost:9092"
aq_topic_name = "aq-api-ingestion-topic"
cities_topic_name = "cities-infos-topic"
hdfs_url = "hdfs://localhost:9870"
hdfs_data_path = "/user/panemiele/data"
hdfs_save_mode = "ErrorIfExists"
hdfs_checkpoint_location = "/tmp/checkpoint/streamingCheckpoint"

neo4j_format = "org.neo4j.spark.DataSource"
neo4j_url = "neo4j+s://de233a56.databases.neo4j.io"
neo4j_save_mode = "Overwrite"
neo4j_checkpoint_location = "/tmp/checkpoint/neo4jCheckpoint"

openstreetmap_url_basepath = "http://nominatim.openstreetmap.org/reverse"

schema = StructType([
    StructField("city", StringType()),
    StructField("coordinates", StructType([
        StructField("latitude", DoubleType()),
        StructField("longitude", DoubleType())
    ])),
    StructField("country", StringType()),
    StructField("location", StringType()),
    StructField("measurements", ArrayType(StructType([
        StructField("lastUpdated", StringType()),
        StructField("parameter", StringType()),
        StructField("unit", StringType()),
        StructField("value", DoubleType())
    ])))
])

# --------------------------------------------------------------------------------------------------#
spark_session = startSparkSession(app_name)
kafkaStreamReader = subscribeToKafkaStreamingTopic(kafka_host_port, aq_topic_name)
get_city_from_lat_lon_udf = udf(lambda lat, lon: findCityByCoordinates(lat, lon), StringType())

# Writes the json retrieved from Kafka topic inside both HDFS and Neo4j

query = kafkaStreamReader \
    .withColumn("json", from_json(col("value").cast("string"), schema)) \
    .withColumn("location", col("json.location")) \
    .withColumn("country", col("json.country")) \
    .withColumn("latitude", col("json.coordinates.latitude")) \
    .withColumn("longitude", col("json.coordinates.longitude")) \
    .withColumn("city", get_city_from_lat_lon_udf(col("latitude"), col("longitude"))) \
    .withColumn("explMeas", explode(col("json.measurements"))) \
    .withColumn("lastUpdated", col("explMeas.lastUpdated")) \
    .withColumn("parameter", col("explMeas.parameter")) \
    .withColumn("value", col("explMeas.value")) \
    .withColumn("unit", col("explMeas.unit"))

queryAQCityInfo = query \
    .select("country", "location", "city") \
    .writeStream

queryMeasurement = query \
    .select("city", "lastUpdated", "parameter", "value", "unit") \
    .writeStream

# console_query = writeInConsole(query)
# hdfs_query = writeStreamingInHdfs(query)
# neo4j_aqcityinfo_query = writeStreamingAQCityInfoInNeo4j(queryAQCityInfo)
# neo4j_measurement_query = writeStreamingMeasurementInNeo4j(queryMeasurement)
# neo4j_relationships_query = writeStreamingRelationshipsInNeo4j(query.writeStream)
spark_session.streams.awaitAnyTermination()
