#!/usr/bin/env python3

"""spark application"""
import argparse
import re
import requests
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType


def findCityByCoordinates(latitude, longitude):
    parameters = {
        'format': 'json',
        'lat': str(latitude),
        'lon': str(longitude)
    }
    try:
        response = requests.get(openstreetmap_url_basepath, params=parameters)
        address = response.json()['address']
        if 'city' in address:
            return address['city']
        elif 'town' in address:
            return address['town']
        else:
            return '---'
    except Exception as ex:
        print('Exception in retrieving city' + str(ex))


openstreetmap_url_basepath = "http://nominatim.openstreetmap.org/reverse"
regex = ",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)"
get_city_from_lat_lon_udf = udf(lambda lat, lon: findCityByCoordinates(lat, lon), StringType())

# create parser and set its arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input_path", type=str, help="Input file path")
parser.add_argument("--output_path", type=str, help="Output folder path")

# parse arguments
args = parser.parse_args()
# input_filepath, output_filepath = args.input_path, args.output_path
input_filepath = "file:///mnt/c/MieiProgrammi/part-00000-02db93fe-c9ef-41e4-adcb-5d2abe67d4b6-c000.json"
output_filepath = "file:///mnt/c/MieiProgrammi/output"

start_time = time.time()

# initialize SparkSession with the proper configuration
spark = SparkSession \
    .builder \
    .appName("Job3 Spark") \
    .config("spark.executor.instances", 15) \
    .getOrCreate()

# read the input file and obtain an RDD with a record for each line
rdd = spark.read.option("multiline", "true").json(input_filepath).cache()
mappedRdd = rdd.toDF("coordinates", "country", "location", "measurements") \
    .withColumn("latitude", col("coordinates.latitude")) \
    .withColumn("longitude", col("coordinates.longitude")) \
    .withColumn("city", get_city_from_lat_lon_udf(col("latitude"), col("longitude"))) \
    .select("country", "city") \
    .show()

# remove csv header
removedHeaderRDD = rdd.filter(f=lambda word: not word.startswith("Id") and not word.endswith("Text"))

# Filtra le righe con uno score >= 4
filteredScoreRDD = removedHeaderRDD.filter(f=lambda line: int(re.split(regex, line)[6]) >= 4)

# Crea la coppia (userId, productId) per ogni riga
user2ProductsRDD = filteredScoreRDD.map(f=lambda line: (re.split(regex, line)[2], re.split(regex, line)[1]))

# Raggruppa i prodotti per utente
userProductsRDD = user2ProductsRDD.groupByKey().mapValues(set)

# Filtra gli utenti con almeno 3 prodotti
activeUsersRDD = userProductsRDD.filter(lambda line: len(line[1]) >= 3).cache()

groupByRDD = activeUsersRDD \
    .groupBy(lambda x: frozenset.intersection(frozenset(x[1]))) \
    .filter(lambda x: len(x[1]) >= 3 & len(x[0]) >= 2)

mappedValuesRDD = groupByRDD.map(lambda x: (set(x[0]), x[1])).mapValues(list).mapValues(lambda x: [y[0] for y in x])
invertedRDD = mappedValuesRDD.map(lambda x: (x[1], x[0]))
resultRDD = invertedRDD.sortBy(lambda x: x[0][0])

resultRDD.collect()
end_time = time.time()
print("Total execution time: {} seconds".format(end_time - start_time))
resultRDD.saveAsTextFile(output_filepath)
