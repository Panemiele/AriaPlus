# AriaPlus
Utilizzando un'architettura a Data Fabric, il progetto mira ad integrare dati provenienti da sensori dislocati su tutto il globo per fornire una panoramica sulla qualità dell'aria e sull'impatto ambientale delle città del mondo.

## Come avviare il progetto

### Requisiti
- Zookeeper
- Kafka
- Spark
- Python
- Java


<br><br><br>


### 1) Avviare Zookeeper e Kafka
Per avviare i server Zookeeper e Kafka è necessario lanciare questi due comandi nell'ordine specificato:

**Per Linux**
1) **Server Zookeeper**: $KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties
2) **Server Kafka**: $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties

**Per Windows**
1) **Server Zookeeper**: %KAFKA_HOME%\bin\windows\zookeeper-server-start.bat %KAFKA_HOME%\config\zookeeper.properties
2) **Server Kafka**: %KAFKA_HOME%\bin\windows\kafka-server-start.bat %KAFKA_HOME%\config\server.properties


<br><br><br>


### 2) Creare topic Kafka
La creazione delle due topic Kafka avviene utilizzando due semplici comandi:

**Per Linux**<br>
- $KAFKA_HOME/bin/kafka-topics.sh --create --topic aq-api-ingestion-topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1<br>
- $KAFKA_HOME/bin/kafka-topics.sh --create --topic cities-infos-topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1

**Per Windows**<br>
- %KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic aq-api-ingestion-topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1<br>
- %KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic cities-infos-topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1

<br><br>

Per verificare la creazione delle topic, è possibile lanciare questo comando:

**Per Linux**
  - $KAFKA_HOME/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

**Per Windows**
  - %KAFKA_HOME%\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

<br><br>

E' possibile creare dei Producer e Consumer per testare il corretto funzionamento delle topic; per farlo, si possono utilizzare i seguenti comandi:

**Per Linux**
- PRODUCER<br>
  - $KAFKA_HOME/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic aq-api-ingestion-topic
  - $KAFKA_HOME/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic cities-infos-topic

- CONSUMER
  - $KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic aq-api-ingestion-topic --from-beginning
  - $KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic cities-infos-topic --from-beginning

**Per Windows**
- PRODUCER
  - %KAFKA_HOME%\bin\windows\kafka-console-producer.bat --broker-list localhost:9092 --topic aq-api-ingestion-topic
  - %KAFKA_HOME%\bin\windows\kafka-console-producer.bat --broker-list localhost:9092 --topic cities-infos-topic

- CONSUMER
  - %KAFKA_HOME%\bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic aq-api-ingestion-topic --from-beginning
  - %KAFKA_HOME%\bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic cities-infos-topic --from-beginning

<br><br><br>

### 3) Avviare streamingIngestionUtil.py via PySpark

### Avviare OpenAQ.py
