# Data Collection

According to the [official documentation](https://drive.google.com/file/d/10r6cnJ5cJ89fPWCgj7j4LtLBqYN9RiI9/view)
Google provides the traces as BigQuery tables or JSON files. Currently, only JSON
files are freely available. Thus, we use the `download` command to downoload the
traces as JSON files and store them locally.

Example:

* Download 10% of instance usage data from cluster a
* Store data in `./instance_usage` folder

```sh
gtd download -pct 10 a instance_usage ./instance_usage
```

Help:

```sh
gtd download --help
```

```sh
usage: gtd download [-h] [-pct PCT] cluster table dst

positional arguments:
  cluster     cluster of the requested trace [a, b, c, d, e, f, g, h]
  table       table of the requested trace [collection_events, instance_events, instance_usage, machine_attributes, machine_events]
  dst         destination folder to store the data

optional arguments:
  -h, --help  show this help message and exit
  -pct PCT    percentage of the dataset to download [1-100] (default: 100)
```
