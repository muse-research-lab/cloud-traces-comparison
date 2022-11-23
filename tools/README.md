# Google Cloud Trace Tools

## Requirements

1. Install `python3` and `pip`
2. Install `gunzip`
3. Install required packages

    ```sh
    pip install -r requirements.txt
    ```

## Data Collection

According to the [official documentation](https://drive.google.com/file/d/10r6cnJ5cJ89fPWCgj7j4LtLBqYN9RiI9/view)
Google provides the traces as BigQuery tables or JSON files. Currently, only JSON
files are freely available. Thus, we create `downloader.py` script that downloads
the traces as JSON files and stores them locally.

Example:

* Download 10% of instance usage data from cluster a
* Store data in `./instance_usage` folder

```sh
python3 downloader.py -pct 10 a instance_usage ./instance_usage
```

Help:

```sh
python3 downloader.py --help
```

```sh
usage: gtd [-h] [-pct PCT] cluster table dst

Download Google trace data (2019) from GCS

positional arguments:
  cluster     cluster of the requested trace [a, b, c, d, e, f, g, h]
  table       table of the requested trace [collection_events, instance_events, instance_usage, machine_attributes, machine_events]
  dst         destination folder to store the data

optional arguments:
  -h, --help  show this help message and exit
  -pct PCT    percentage of the dataset to download [1-100] (default: 100)
```

## Data Storage

The best way to handle trace data is to store them in an SQL database. This way,
we can execute SQL queries to filter data and perform complex operations. We choose
MySQL as it is a widely supported open source variant of SQL.

After we spin up a database we create the following tables:

```sql
-- Instance Events table
CREATE TABLE IF NOT EXISTS instance_events (
   `time` bigint not null,
   `type` integer not null,
   `collection_id` bigint not null,
   `scheduling_class` integer not null,
   `missing_type` integer,
   `collection_type` integer not null,
   `priority` integer not null,
   `alloc_collection_id` bigint not null,
   `instance_index` bigint not null,
   `machine_id` bigint not null,
   `alloc_instance_index` bigint not null,
   `resource_request` json not null,
   `constraint` json not null
);
```

```sql
-- Instance Usage table
CREATE TABLE IF NOT EXISTS instance_usage (
   `start_time` bigint not null,
   `end_time` bigint not null,
   `collection_id` bigint not null,
   `instance_index` bigint not null,
   `machine_id` bigint not null,
   `alloc_collection_id` bigint not null,
   `alloc_instance_index` bigint,
   `collection_type` integer not null,
   `average_usage` json not null,
   `maximum_usage` json not null,
   `random_sample_usage` json not null,
   `assigned_memory` double precision not null,
   `page_cache_memory` double precision not null,
   `cycles_per_instruction` double precision,
   `memory_accesses_per_instruction` double precision,
   `sample_rate` double precision not null,
   `cpu_usage_distribution` json not null,
   `tail_cpu_usage_distribution` json not null
);
```

We then use `exporter.py` script to store the traces in MySQL.

Example:

* Store instance usage data of a single JSON file
* Use the following database configuration:
    * host: 192.168.0.1
    * port: 3306
    * database: clusterdata_2019_a
    * table: instance_usage
    * user: root
    * password: root

```sh
python3 exporter.py -host 192.168.0.1 -p 3306 -db clusterdata_2019_a -u root -pwd root instance_usage-000000000000.json instance_usage
```

Help:

```sh
python3 exporter.py --help
```

```sh
usage: gtde [-h] -host HOST -p PORT -db DATABASE -u USERNAME -pwd PASSWORD [-r] [-chunk CHUNK] src table

Export Google trace data (2019) to SQL database

positional arguments:
  src            source file path
  table          table of the database [instance_events, instance_usage]

optional arguments:
  -h, --help     show this help message and exit
  -r             replace table flag. If true the table is replaced by the new data, if flase the new data is appended
  -chunk CHUNK   number of rows in each batch to be written at a time (default: 200000)

required named arguments:
  -host HOST     host name or IP of the database server
  -p PORT        port of the database server
  -db DATABASE   name of the database
  -u USERNAME    user of the database
  -pwd PASSWORD  password of the database user
```

**Disclaimers:**

* We currently support instance usage and events data, because Google's *Overcommit
  Simulator* uses only these tables
* We currently target only MySQL
* We store timestamps as integers and they express Unix timestamps in microseconds(us)
