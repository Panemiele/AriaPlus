import requests
import traceback
from decouple import config
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf, explode, count
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, DoubleType, FloatType


#####################
# Functions section #
#####################

def neo4jStreamingBaseOptions(data_frame):
    return data_frame \
        .format(neo4j_format) \
        .option("url", neo4j_url) \
        .option("save.mode", neo4j_save_mode) \
        .option("checkpointLocation", neo4j_checkpoint_location) \
        .option("authentication.basic.username", config("neo4j_username")) \
        .option("authentication.basic.password", config("neo4j_password"))


def writeStreamingInHdfs(data_frame):
    return data_frame \
        .format("json") \
        .trigger(processingTime="10 seconds") \
        .option("url", hdfs_url) \
        .option("path", hdfs_data_path) \
        .option("checkpointLocation", hdfs_checkpoint_location) \
        .start()


def writeStreamingAQCityInfoInNeo4j(data_frame):
    return neo4jStreamingBaseOptions(data_frame) \
        .option("labels", "AQCityInfo") \
        .option("node.keys", "city") \
        .start()


def writeStreamingMeasurementInNeo4j(data_frame):
    return neo4jStreamingBaseOptions(data_frame) \
        .option("labels", "Measurement") \
        .option("node.keys", "parameter,city,lastUpdated") \
        .start()


def writeStreamingCitiesInfoInNeo4j(data_frame):
    return neo4jStreamingBaseOptions(data_frame) \
        .option("labels", "City") \
        .option("node.keys", "city") \
        .start()


# Used to debug data frame
def writeInConsole(data_frame):
    return data_frame.format("console").option("truncate", "false").start()


def writeStreamingAQRelationshipsInNeo4j(data_frame):
    cypher_query = """
        MATCH (aq:AQCityInfo), (m:Measurement)
        WHERE aq.city = m.city
        MERGE (m)-[:IS_MEASUREMENT_OF]->(aq)
    """
    return neo4jStreamingBaseOptions(data_frame) \
        .option("query", cypher_query) \
        .start()


def writeStreamingCitiesRelationshipsInNeo4j(data_frame):
    cypher_query = """
        MATCH (c:City)
        WITH c
        MATCH (aq:AQCityInfo) 
        WHERE aq.city = c.city and aq.country = c.iso2
        MERGE (aq)-[:REPRESENTS]->(c)
    """
    return neo4jStreamingBaseOptions(data_frame) \
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
neo4j_save_mode = "ErrorIfExists"
neo4j_checkpoint_location = "/tmp/checkpoint/neo4jCheckpoint"

openstreetmap_url_basepath = "http://nominatim.openstreetmap.org/reverse"

aq_schema = StructType([
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

csv_cities_schema = StructType([
    StructField("name", StringType()),
    StructField("city_ascii", StringType()),
    StructField("latitude", FloatType()),
    StructField("longitude", FloatType()),
    StructField("country", StringType()),
    StructField("iso2", StringType()),
    StructField("iso3", StringType()),
    StructField("admin_name", StringType()),
    StructField("capital", StringType()),
    StructField("population", DoubleType()),
    StructField("id", StringType())
])

# --------------------------------------------------------------------------------------------------#
spark_session = startSparkSession(app_name)
aq_kafkaStreamReader = subscribeToKafkaStreamingTopic(kafka_host_port, aq_topic_name)
cities_kafkaStreamReader = subscribeToKafkaStreamingTopic(kafka_host_port, cities_topic_name)
get_city_from_lat_lon_udf = udf(lambda lat, lon: findCityByCoordinates(lat, lon), StringType())

# Writes the json retrieved from Kafka topic inside both HDFS and Neo4j


query_without_city = aq_kafkaStreamReader \
    .withColumn("json", from_json(col("value").cast("string"), aq_schema)) \
    .withColumn("location", col("json.location")) \
    .withColumn("country", col("json.country")) \
    .withColumn("latitude", col("json.coordinates.latitude")) \
    .withColumn("longitude", col("json.coordinates.longitude"))

# Used to execute the mapping between coordinates and cities
# (NB: Nominatim OpenStreetMap is very slow, so this piece of code is not used anymore
#-------------------------------------------------------------------------------------------------------------
#
# query = query_without_city.withColumn("city", get_city_from_lat_lon_udf(col("latitude"), col("longitude")))
#
#-------------------------------------------------------------------------------------------------------------

query = query_without_city.withColumn("city", col("json.city"))

queryAQCityInfo = query \
    .select("country", "location", "city") \
    .writeStream

queryMeasurement = query \
    .withColumn("explMeas", explode(col("json.measurements"))) \
    .withColumn("lastUpdated", col("explMeas.lastUpdated")) \
    .withColumn("parameter", col("explMeas.parameter")) \
    .withColumn("value", col("explMeas.value")) \
    .withColumn("unit", col("explMeas.unit")) \
    .select("city", "lastUpdated", "parameter", "value", "unit") \
    .writeStream

queryCitiesInformations = cities_kafkaStreamReader \
    .withColumn("json", from_json(col("value").cast("string"), csv_cities_schema)) \
    .withColumn("city", col("json.name")) \
    .withColumn("country", col("json.country")) \
    .withColumn("iso2", col("json.iso2")) \
    .withColumn("population", col("json.population")) \
    .withColumn("latitude", col("json.latitude")) \
    .withColumn("longitude", col("json.longitude")) \
    .select("city", "country", "population", "latitude", "longitude", "iso2") \
    .writeStream


# Used to print the query in the console
# console_query = writeInConsole(queryAQCityInfo)

# Used to add the json file in HDFS
hdfs_query = writeStreamingInHdfs(queryAQCityInfo)

# Used to add Air Quality Cities' infos in Neo4j
neo4j_aqcityinfo_query = writeStreamingAQCityInfoInNeo4j(queryAQCityInfo)

# Used to add Air Quality Cities' measurements in Neo4j
neo4j_measurement_query = writeStreamingMeasurementInNeo4j(queryMeasurement)

# Used to add AQ relationships in Neo4j
neo4j_aq_relationships_query = writeStreamingAQRelationshipsInNeo4j(query.writeStream)

# Used to add Cities' infos in Neo4j
neo4j_cities_info_query = writeStreamingCitiesInfoInNeo4j(queryCitiesInformations)

# Used to add relationships between AQ and cities in Neo4j
neo4j_cities_relationships_query = writeStreamingCitiesRelationshipsInNeo4j(query.writeStream)

spark_session.streams.awaitAnyTermination()
