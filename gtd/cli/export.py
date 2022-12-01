import argparse

import pandas as pd

from gtd.cli.commands import Command
from gtd.cli.utils import create_mysql_con


class ExportCommand(Command):
    def run(self, args: argparse.Namespace) -> int:
        print("Reading source file data...")
        data = pd.read_json(args.src, lines=True, date_unit="us")

        if args.table == "instance_events":
            print("Preprocessing data...")
            preprocessed_data = self._preprocess_instance_events(data)
            print("Transforming data...")
            transformed_data = self._transform_instance_events(
                preprocessed_data
            )
            print("Validating data...")
            final_data = self._validate_instance_events(transformed_data)
        elif args.table == "instance_usage":
            print("Preprocessing data...")
            preprocessed_data = self._preprocess_instance_usg(data)
            print("Transforming data...")
            transformed_data = self._transform_instance_usg(preprocessed_data)
            print("Validating data...")
            final_data = self._validate_instance_usg(transformed_data)
        else:
            raise ValueError(f"{args.table} is not a valid table name!")

        con = create_mysql_con(
            args.host, args.port, args.username, args.password, args.database
        )

        if args.replace:
            policy = "replace"
        else:
            policy = "append"
        print(
            f"""
            Sending data... ({policy} - {final_data.shape[0]} records)
            """
        )
        final_data.to_sql(
            args.table,
            con,
            if_exists=policy,
            index=False,
            chunksize=args.chunksize,
        )
        return 0

    def _preprocess_instance_events(
        self, df_events: pd.DataFrame
    ) -> pd.DataFrame:
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
        # - alloc_collection_id (0 means not running in alloc set or it is an alloc set) # noqa: E501
        # - alloc_instance_index (0 means index=0, the first index in a 0-based index) # noqa: E501
        #   Note: Zero (0) values seem to appear as NaN values probably because of unset JSON fields # noqa: E501
        df_events["machine_id"] = df_events["machine_id"].fillna(0)
        df_events["alloc_collection_id"] = df_events[
            "alloc_collection_id"
        ].fillna(0)
        df_events["alloc_instance_index"] = df_events[
            "alloc_instance_index"
        ].fillna(0)

        return df_events

    def _transform_instance_events(
        self, df_events: pd.DataFrame
    ) -> pd.DataFrame:
        # Convert to the desired field types
        df_events["time"] = df_events["time"].astype("int64")
        df_events["type"] = df_events["type"].astype("int")
        df_events["collection_id"] = df_events["collection_id"].astype("int64")
        df_events["scheduling_class"] = df_events["scheduling_class"].astype(
            "int"
        )
        df_events["missing_type"] = df_events["missing_type"].astype("float64")
        df_events["collection_type"] = df_events["collection_type"].astype(
            "int"
        )
        df_events["priority"] = df_events["priority"].astype("int64")
        df_events["alloc_collection_id"] = df_events[
            "alloc_collection_id"
        ].astype("int64")
        df_events["instance_index"] = df_events["instance_index"].astype(
            "int64"
        )
        df_events["machine_id"] = df_events["machine_id"].astype("int64")
        df_events["alloc_instance_index"] = df_events[
            "alloc_instance_index"
        ].astype("int64")

        # Transform objects to strings - e.g. '{ "cpus": 0.09, "memory": 0.01 }' # noqa: E501
        df_events["resource_request"] = df_events["resource_request"].astype(
            "str"
        )
        df_events["constraint"] = df_events["constraint"].astype("str")

        df_events["resource_request"] = df_events["resource_request"].apply(
            lambda x: x.replace("'", '"')
        )
        df_events["constraint"] = df_events["constraint"].apply(
            lambda x: x.replace("'", '"')
        )

        return df_events

    def _validate_instance_events(
        self, df_events: pd.DataFrame
    ) -> pd.DataFrame:
        # Keep rows with values in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] for type field # noqa: E501
        df_events = df_events[df_events["type"].isin(range(0, 11))]

        # Keep rows with values in [0, 1, 2, 3] for scheduling_class field
        df_events = df_events[df_events["scheduling_class"].isin(range(0, 4))]

        # Keep rows with values in [0, 1, 2, 3, NaN] for missing_type field
        df_events = df_events[
            (df_events["missing_type"].isin(range(0, 4)))
            | (df_events["missing_type"].isna())
        ]

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

    def _preprocess_instance_usg(self, df_usage: pd.DataFrame) -> pd.DataFrame:
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

        # Check if the following rows exists and if not initiate them
        # - cycles_per_instruction (NaN values allowed)
        # - memory_accesses_per_instruction (NaN values allowed)
        if "cycles_per_instruction" not in df_usage.columns:
            df_usage["cycles_per_instruction"] = None
        if "memory_accesses_per_instruction" not in df_usage.columns:
            df_usage["memory_accesses_per_instruction"] = None

        return df_usage

    def _transform_instance_usg(self, df_usage: pd.DataFrame) -> pd.DataFrame:
        # Convert to the desired field types
        df_usage["start_time"] = df_usage["start_time"].astype("int64")
        df_usage["end_time"] = df_usage["end_time"].astype("int64")
        df_usage["collection_id"] = df_usage["collection_id"].astype("int64")
        df_usage["instance_index"] = df_usage["instance_index"].astype("int64")
        df_usage["machine_id"] = df_usage["machine_id"].astype("int64")
        df_usage["alloc_collection_id"] = df_usage[
            "alloc_collection_id"
        ].astype("int64")
        df_usage["alloc_instance_index"] = df_usage[
            "alloc_instance_index"
        ].astype("float64")
        df_usage["collection_type"] = df_usage["collection_type"].astype("int")

        df_usage["assigned_memory"] = df_usage["assigned_memory"].astype(
            "float64"
        )
        df_usage["page_cache_memory"] = df_usage["page_cache_memory"].astype(
            "float64"
        )
        df_usage["cycles_per_instruction"] = df_usage[
            "cycles_per_instruction"
        ].astype("float64")
        df_usage["memory_accesses_per_instruction"] = df_usage[
            "memory_accesses_per_instruction"
        ].astype("float64")
        df_usage["sample_rate"] = df_usage["sample_rate"].astype("float64")

        # Transform objects to strings - e.g. '{ "cpus": 0.09, "memory": 0.01 }' # noqa: E501
        df_usage["average_usage"] = df_usage["average_usage"].astype("str")
        df_usage["maximum_usage"] = df_usage["maximum_usage"].astype("str")
        df_usage["random_sample_usage"] = df_usage[
            "random_sample_usage"
        ].astype("str")
        df_usage["cpu_usage_distribution"] = df_usage[
            "cpu_usage_distribution"
        ].astype("str")
        df_usage["tail_cpu_usage_distribution"] = df_usage[
            "tail_cpu_usage_distribution"
        ].astype("str")

        df_usage["average_usage"] = df_usage["average_usage"].apply(
            lambda x: x.replace("'", '"')
        )
        df_usage["maximum_usage"] = df_usage["maximum_usage"].apply(
            lambda x: x.replace("'", '"')
        )
        df_usage["random_sample_usage"] = df_usage["random_sample_usage"].apply(
            lambda x: x.replace("'", '"')
        )
        df_usage["cpu_usage_distribution"] = df_usage[
            "cpu_usage_distribution"
        ].apply(lambda x: x.replace("'", '"'))
        df_usage["tail_cpu_usage_distribution"] = df_usage[
            "tail_cpu_usage_distribution"
        ].apply(lambda x: x.replace("'", '"'))

        return df_usage

    def _validate_instance_usg(self, df_usage: pd.DataFrame) -> pd.DataFrame:
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
        df_usage = df_usage[
            (df_usage["cycles_per_instruction"] >= 0)
            | (df_usage["cycles_per_instruction"].isna())
        ]
        df_usage = df_usage[
            (df_usage["memory_accesses_per_instruction"] >= 0)
            | (df_usage["memory_accesses_per_instruction"].isna())
        ]

        # Keep rows with -1 or greater values for the following fields
        # - machine_id
        # - alloc_instance_index (NaN values allowed)
        df_usage = df_usage[df_usage["machine_id"] >= -1]
        df_usage = df_usage[
            (df_usage["alloc_instance_index"] >= -1)
            | (df_usage["alloc_instance_index"].isna())
        ]

        # Keep rows with values between 0 and 1 (inclusive) for the following fields: # noqa: E501
        # - assigned_memory
        # - page_cache_memory
        # - sample_rate
        df_usage = df_usage[
            (df_usage["assigned_memory"] >= 0)
            | (df_usage["assigned_memory"] <= 1)
        ]
        df_usage = df_usage[
            (df_usage["page_cache_memory"] >= 0)
            | (df_usage["page_cache_memory"] <= 1)
        ]
        df_usage = df_usage[
            (df_usage["sample_rate"] >= 0) | (df_usage["sample_rate"] <= 1)
        ]

        return df_usage
