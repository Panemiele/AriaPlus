from pyspark.sql import SparkSession


#####################
# Functions section #
#####################

def startSparkSession(appName):
    return SparkSession \
        .builder \
        .appName(appName) \
        .getOrCreate()


def subscribeToKafkaStreamingTopic(appName, host_port, topic_name):
    try:
        return startSparkSession(appName) \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", host_port) \
            .option("subscribe", topic_name) \
            .load()
    except Exception as e:
        print(e)


# --------------------------------------------------------------------------------------------------#
app_name = "ingestion-util"
kafka_host_port = "localhost:9092"
topic_name = "streaming-ingestion-topic"
neo4j_format = "org.neo4j.spark.DataSource"
neo4j_url = "bolt://localhost:7687"
hdfs_url = "hdfs://localhost:9870"
hdfs_save_mode = "ErrorIfExists"
hdfs_checkpoint_location = "/tmp/checkpoint/streamingCheckpoint"

kafkaStreamReader = subscribeToKafkaStreamingTopic(app_name, kafka_host_port, topic_name)

query = kafkaStreamReader \
    .writeStream \
    .format(neo4j_format) \
    .option("url", neo4j_url) \
    .option("save.mode", hdfs_save_mode) \
    .option("checkpointLocation", hdfs_checkpoint_location) \
    .option("labels", "AirQuality") \
    .option("node.keys", "value") \
    .start()
