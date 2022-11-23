import argparse

import numpy as np
import pandas as pd

from sqlalchemy import create_engine

def get_args():
    parser = argparse.ArgumentParser(
        prog="gtde",
        description="Export Google trace data (2019) to SQL database"
    )

    parser.add_argument(
        "src",
        metavar="src",
        type=str,
        help="source file path",
    )

    parser.add_argument(
        "table",
        metavar="table",
        type=str,
        choices=["instance_events", "instance_usage"],
        help="table of the database [instance_events, instance_usage]",
    )

    requiredNamed = parser.add_argument_group('required named arguments')

    requiredNamed.add_argument(
        "-host",
        dest="host",
        type=str,
        required=True,
        help=(
            "host name or IP of the database server"
        ),
    )

    requiredNamed.add_argument(
        "-p",
        dest="port",
        type=int,
        required=True,
        help=(
            "port of the database server"
        ),
    )

    requiredNamed.add_argument(
        "-db",
        dest="database",
        type=str,
        required=True,
        help=(
            "name of the database"
        ),
    )

    requiredNamed.add_argument(
        "-u",
        dest="username",
        type=str,
        required=True,
        help=(
            "user of the database"
        ),
    )

    requiredNamed.add_argument(
        "-pwd",
        dest="password",
        type=str,
        required=True,
        help=(
            "password of the database user"
        ),
    )

    parser.add_argument(
        "-r",
        dest="replace",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help=(
            "replace table flag. If true the table is replaced by the new data, if flase the new data is appended"
        ),
    )

    parser.add_argument(
        "-chunk",
        dest="chunksize",
        type=int,
        required=False,
        default=200000,
        metavar="CHUNK",
        help=(
            "number of rows in each batch to be written at a time (default: 200000)"
        ),
    )

    return parser.parse_args()

def read_src(src_file):
    return pd.read_json(src_file, lines=True, date_unit="us")

def create_connection(host, port, username, password, database):
    db_string = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
    db = create_engine(db_string)
    return db.connect()

def preprocess_instance_events(df_events):
    # Keep rows without null values for the following fields:
    # - time
    # - collection_id
    # - instance_index
    # Note: These are the parts of the composite primary key
    df_events = df_events[df_events["time"].notnull()]
    df_events = df_events[df_events["collection_id"].notnull()]
    df_events = df_events[df_events["instance_index"].notnull()]

    # Keep rows without nan values for json objects of resource requests
    df_events = df_events[df_events["resource_request"].notna()]

    # Transform null fields to 0 for the following fields:
    # - machine_id (0 means not scheduled)
    # - alloc_collection_id (0 means not running in alloc set or it is an alloc set)
    # - alloc_instance_index (0 means index=0, the first index in a 0-based index)
    #   Note: Zero (0) values seem to appear as NaN values probably because of unset JSON fields
    df_events['machine_id'] = df_events['machine_id'].fillna(0)
    df_events['alloc_collection_id'] = df_events['alloc_collection_id'].fillna(0)
    df_events['alloc_instance_index'] = df_events['alloc_instance_index'].fillna(0)

    return df_events

def transform_instance_events(df_events):
    # Convert to the desired field types
    df_events["time"] = df_events["time"].astype("int64")
    df_events["type"] = df_events["type"].astype("int")
    df_events["collection_id"] = df_events["collection_id"].astype("int64")
    df_events["scheduling_class"] = df_events["scheduling_class"].astype("int")
    df_events["missing_type"] = df_events["missing_type"].astype("float64")
    df_events["collection_type"] = df_events["collection_type"].astype("int")
    df_events["priority"] = df_events["priority"].astype("int64")
    df_events["alloc_collection_id"] = df_events["alloc_collection_id"].astype("int64")
    df_events["instance_index"] = df_events["instance_index"].astype("int64")
    df_events["machine_id"] = df_events["machine_id"].astype("int64")
    df_events["alloc_instance_index"] = df_events["alloc_instance_index"].astype("int64")

    # Transform objects to strings - e.g. '{ "cpus": 0.09, "memory": 0.01 }'
    df_events["resource_request"] = df_events["resource_request"].astype("str")
    df_events["constraint"] = df_events["constraint"].astype("str")

    df_events["resource_request"] = df_events["resource_request"].apply(lambda x: x.replace("'", '"'))
    df_events["constraint"] = df_events["constraint"].apply(lambda x: x.replace("'", '"'))

    return df_events

def validate_instance_events(df_events):
    # Keep rows with values in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] for type field
    df_events = df_events[df_events["type"].isin(range(0, 11))]

    # Keep rows with values in [0, 1, 2, 3] for scheduling_class field
    df_events = df_events[df_events["scheduling_class"].isin(range(0, 4))]

    # Keep rows with values in [0, 1, 2, 3, NaN] for missing_type field
    df_events = df_events[(df_events["missing_type"].isin(range(0, 4))) | (df_events["missing_type"].isna())]

    # Keep rows with values in [0, 1] for collection_type field
    df_events = df_events[df_events["collection_type"].isin([0, 1])]

    # Keep rows with zero or positive values for the following fields:
    # - time
    # - collection_id
    # - priority
    # - alloc_collection_id
    # - instance_index
    df_events = df_events[df_events["time"] >= 0]
    df_events = df_events[df_events["collection_id"] >= 0]
    df_events = df_events[df_events["priority"] >= 0]
    df_events = df_events[df_events["alloc_collection_id"] >= 0]
    df_events = df_events[df_events["instance_index"] >= 0]

    # Keep rows with -1 or greater values for the following fields
    # - machine_id
    # - alloc_instance_index
    df_events = df_events[df_events["machine_id"] >= -1]
    df_events = df_events[df_events["alloc_instance_index"] >= -1]

    return df_events

def preprocess_instance_usage(df_usage):
    # Keep rows without null values for the following fields:
    # - start_time
    # - end_time
    # - collection_id
    # - instance_index
    # Note: These are the parts of the composite primary key
    df_usage = df_usage[df_usage["start_time"].notnull()]
    df_usage = df_usage[df_usage["end_time"].notnull()]
    df_usage = df_usage[df_usage["collection_id"].notnull()]
    df_usage = df_usage[df_usage["instance_index"].notnull()]

    return df_usage

def transform_instance_usage(df_usage):
    # Convert to the desired field types
    df_usage["start_time"] = df_usage["start_time"].astype("int64")
    df_usage["end_time"] = df_usage["end_time"].astype("int64")
    df_usage["collection_id"] = df_usage["collection_id"].astype("int64")
    df_usage["instance_index"] = df_usage["instance_index"].astype("int64")
    df_usage["machine_id"] = df_usage["machine_id"].astype("int64")
    df_usage["alloc_collection_id"] = df_usage["alloc_collection_id"].astype("int64")
    df_usage["alloc_instance_index"] = df_usage["alloc_instance_index"].astype("float64")
    df_usage["collection_type"] = df_usage["collection_type"].astype("int")

    df_usage["assigned_memory"] = df_usage["assigned_memory"].astype("float64")
    df_usage["page_cache_memory"] = df_usage["page_cache_memory"].astype("float64")
    df_usage["cycles_per_instruction"] = df_usage["cycles_per_instruction"].astype("float64")
    df_usage["memory_accesses_per_instruction"] = df_usage["memory_accesses_per_instruction"].astype("float64")
    df_usage["sample_rate"] = df_usage["sample_rate"].astype("float64")

    # Transform objects to strings - e.g. '{ "cpus": 0.09, "memory": 0.01 }'
    df_usage["average_usage"] = df_usage["average_usage"].astype("str")
    df_usage["maximum_usage"] = df_usage["maximum_usage"].astype("str")
    df_usage["random_sample_usage"] = df_usage["random_sample_usage"].astype("str")
    df_usage["cpu_usage_distribution"] = df_usage["cpu_usage_distribution"].astype("str")
    df_usage["tail_cpu_usage_distribution"] = df_usage["tail_cpu_usage_distribution"].astype("str")

    df_usage["average_usage"] = df_usage["average_usage"].apply(lambda x: x.replace("'", '"'))
    df_usage["maximum_usage"] = df_usage["maximum_usage"].apply(lambda x: x.replace("'", '"'))
    df_usage["random_sample_usage"] = df_usage["random_sample_usage"].apply(lambda x: x.replace("'", '"'))
    df_usage["cpu_usage_distribution"] = df_usage["cpu_usage_distribution"].apply(lambda x: x.replace("'", '"'))
    df_usage["tail_cpu_usage_distribution"] = df_usage["tail_cpu_usage_distribution"].apply(lambda x: x.replace("'", '"'))

    return df_usage

def validate_instance_usage(df_usage):
    # Keep rows with values in [0, 1] for collection_type field
    df_usage = df_usage[df_usage["collection_type"].isin([0, 1])]

    # Keep rows with zero or positive values for the following fields:
    # - start_time
    # - end_time
    # - collection_id
    # - instance_index
    # - alloc_collection_id
    # - cycles_per_instruction (NaN values allowed)
    # - memory_accesses_per_instruction (NaN values allowed)
    df_usage = df_usage[df_usage["start_time"] >= 0]
    df_usage = df_usage[df_usage["end_time"] >= 0]
    df_usage = df_usage[df_usage["collection_id"] >= 0]
    df_usage = df_usage[(df_usage["cycles_per_instruction"] >= 0) | (df_usage["cycles_per_instruction"].isna())]
    df_usage = df_usage[(df_usage["memory_accesses_per_instruction"] >= 0) | (df_usage["memory_accesses_per_instruction"].isna())]

    # Keep rows with -1 or greater values for the following fields
    # - machine_id
    # - alloc_instance_index (NaN values allowed)
    df_usage = df_usage[df_usage["machine_id"] >= -1]
    df_usage = df_usage[(df_usage["alloc_instance_index"] >= -1) | (df_usage["alloc_instance_index"].isna())]

    # Keep rows with values between 0 and 1 (inclusive) for the following fields:
    # - assigned_memory
    # - page_cache_memory
    # - sample_rate
    df_usage = df_usage[(df_usage["assigned_memory"] >= 0) | (df_usage["assigned_memory"] <= 1)]
    df_usage = df_usage[(df_usage["page_cache_memory"] >= 0) | (df_usage["page_cache_memory"] <= 1)]
    df_usage = df_usage[(df_usage["sample_rate"] >= 0) | (df_usage["sample_rate"] <= 1)]

    return df_usage

if __name__ == "__main__":
    args = get_args()

    print("Reading source file data...")
    data = read_src(args.src)

    if args.table == "instance_events":
        print("Preprocessing data...")
        preprocessed_data = preprocess_instance_events(data)
        print("Transforming data...")
        transformed_data = transform_instance_events(preprocessed_data)
        print("Validating data...")
        final_data = validate_instance_events(transformed_data)
    elif args.table == "instance_usage":
        print("Preprocessing data...")
        preprocessed_data = preprocess_instance_usage(data)
        print("Transforming data...")
        transformed_data = transform_instance_usage(preprocessed_data)
        print("Validating data...")
        final_data = validate_instance_usage(transformed_data)
    else:
        raise ValueError(f"{args.table} is not a valid table name!")
    
    con = create_connection(args.host, args.port, args.username, args.password, args.database)

    if args.replace:
        policy = "replace"
    else:
        policy = "append"
    print(f"Sending data to database... ({policy} - {final_data.shape[0]} records)")
    final_data.to_sql(args.table, con, if_exists=policy, index=False, chunksize=args.chunksize)
 