# AriaPlus
Utilizzando un'architettura a Data Fabric, il progetto mira ad integrare dati provenienti da sensori dislocati su tutto il globo per fornire una panoramica sulla qualità dell'aria e sull'impatto ambientale delle città del mondo.

## Come avviare il progetto

### Requisiti
1) Zookeeper
2) Kafka
3) Spark
4) Python
5) Java

### Avviare Zookeeper e Kafka
1) **Server Zookeeper**: $KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties
2) **Server Kafka**: $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties

### Avviare streamingIngestionUtil.py via PySpark

### Avviare OpenAQ.py