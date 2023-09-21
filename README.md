# AriaPlus
Utilizzando un'architettura a Data Fabric, il progetto mira ad integrare dati provenienti da sensori dislocati su tutto il globo per fornire una panoramica sulla qualità dell'aria e sull'impatto ambientale delle città del mondo.

## Come avviare il progetto

### Requisiti
- Zookeeper
- Kafka
- Spark
- Python
- Java 11+
- (Opzionale) Postman


<br><br><br><br>


### 1) Avviare Zookeeper e Kafka
Per avviare i server Zookeeper e Kafka è necessario lanciare questi due comandi nell'ordine specificato:

**Per Linux**
1) **Server Zookeeper**: $KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties
2) **Server Kafka**: $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties

**Per Windows**
1) **Server Zookeeper**: %KAFKA_HOME%\bin\windows\zookeeper-server-start.bat %KAFKA_HOME%\config\zookeeper.properties
2) **Server Kafka**: %KAFKA_HOME%\bin\windows\kafka-server-start.bat %KAFKA_HOME%\config\server.properties


<br><br><br><br>


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

<br><br><br><br>

### 3) Avviare l'istanza di Neo4j
Prima di procedere col prossimo step è necessario avviare un'istanza di Neo4j: https://neo4j.com/
Fatto ciò, sarà necessario cambiare i puntamenti a Neo4j all'interno di **streamingIngestionUtil.py**.

<br><br><br><br>

### 4) Avviare streamingIngestionUtil.py via PySpark
Il passo successivo è quello di avviare **streamingIngestionUtil.py**, lo script Python in ascolto sulle topic Kafka che, tramite **Spark Structured Streaming**, scoda i messaggi, li processa e li instrada verso la Console, **Hadoop** e/o **Neo4j**.
Per farlo, è possibile seguire i seguenti due approcci:
  - Approccio Spark Submit
    1) Aprire una nuova finestra del terminale
    2) navigare fino alla cartella $SPARK_HOME/bin
    3) modificare e lanciare il comando: **spark-submit --master _<local[numeroThread] / yarn>_ <_pathAriaPlus_>/ingestionMS/streamingIngestionUtil.py --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1,org.neo4j:neo4j-connector-apache-spark_2.12:5.0.1_for_spark_3**

    Dove:
    - <local[numeroThread] / yarn> := il master URL per il cluster
    - [numeroThread] := numero di thread da utilizzare per esecuzione in locale (per prestazioni migliori)
    - <_pathAriaPlus_> := il path della cartella "/AriaPlus" all'interno del file system della macchina
<br>

  - Approccio PySpark
    1) Aprire una nuova finestra del terminale
    2) navigare fino alla cartella $SPARK_HOME/bin
    3) lanciare il comando: **pyspark --master local[8] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1,org.neo4j:neo4j-connector-apache-spark_2.12:5.0.1_for_spark_3**
    4) copiare l'intero codice 

<br><br><br><br>

### 5) Avviare OpenAQ.py
Avviato lo script di ingestion, è possibile avviare lo script per estrarre i dati della qulità dell'aria: OpenAQ.py .
Per farlo, basta seguire la stessa guida del passo precedente, adattandola a **OpenAQ.py** anziché a **streamingIngestionUtil.py**.

<br><br><br><br>

### 6) Avviare CityMSApplication
Uno degli ultimi passi da compiere è quello di avviare la Spring boot app **CityMSApplication**; per farlo è necessario seguire i seguenti step:
  - Eseguire una build del progetto via **Maven**
  - Aprire una finestra del terminale
  - lanciare il comando: **java -jar <_pathAriaPlus_>/cityMS/target/cityMS-0.0.1-SNAPSHOT.jar**
    
Dove:
- <_pathAriaPlus_> := il path della cartella "/AriaPlus" all'interno del file system della macchina

<br><br><br><br>

### 7) Contattare l'endpoint di CityMSApplication
Come ultimo passaggio, è necessario contattare l'endpoint di CityMSApplication per attivare il servizio di estrazione dati dal dataset **worldcities.csv** che processerà ed invierà i dati alla topic Kafka.
Per farlo è possibile utilizzare (o importare su **Postman**) la seguente curl: **curl --location --request POST 'http://localhost:8080/send-cities'**
