import argparse
from typing import List, Tuple, Union


def add_download_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "cluster",
        metavar="cluster",
        type=str,
        choices=["a", "b", "c", "d", "e", "f", "g", "h"],
        help="cluster of the requested trace [a, b, c, d, e, f, g, h]",
    )

    parser.add_argument(
        "table",
        metavar="table",
        type=str,
        choices=[
            "collection_events",
            "instance_events",
            "instance_usage",
            "machine_attributes",
            "machine_events",
        ],
        help=(
            """
            table of the requested trace [collection_events, instance_events,
            instance_usage, machine_attributes, machine_events]
            """
        ),
    )

    parser.add_argument(
        "dst",
        metavar="dst",
        type=str,
        help="destination folder to store the data",
    )

    parser.add_argument(
        "-pct",
        metavar="PCT",
        default=100,
        type=int,
        choices=range(1, 101),
        help="percentage of the dataset to download [1-100] (default: 100)",
        dest="pct",
    )


def add_export_args(parser: argparse.ArgumentParser) -> None:
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

    parser.add_argument(
        "-r",
        dest="replace",
        type=bool,
        action=argparse.BooleanOptionalAction,  # type: ignore
        help=(
            """
            replace table flag. If true the table is replaced by the new data,
            if false the new data is appended
            """
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
            """
            number of rows in each batch to be written at a time
            (default: 200000)
            """
        ),
    )


def add_ts_subparsers(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(
        title="available ts subcommands", dest="ts_cmd_name"
    )

    # Create parser for the "ts create" command
    ts_create_parser = subparsers.add_parser(
        "create", help="create time series csv files of instances"
    )
    add_ts_create_args(ts_create_parser)
    add_db_connection_args_group(ts_create_parser)

    # Create parser for the "ts export" command
    ts_export_parser = subparsers.add_parser(
        "export", help="export time series csv files to SQL database"
    )
    add_ts_export_args(ts_export_parser)
    add_db_connection_args_group(ts_export_parser)


def add_ts_create_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "table",
        metavar="table",
        type=str,
        help=("name of the database table to read from"),
    )

    parser.add_argument(
        "input",
        metavar="input",
        type=str,
        help="""
        input file that contains tuples
        (collection_id, instance_index, upper_limit, lower_limit)
        """,
    )

    parser.add_argument(
        "output",
        metavar="output",
        type=str,
        help="output dir to store the csv files",
    )


def add_ts_export_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "input",
        metavar="input",
        type=str,
        help="input dir that contains time series files",
    )

    parser.add_argument(
        "output",
        metavar="output",
        type=str,
        help="output database table to store time series data",
    )


def add_db_connection_args_group(parser: argparse.ArgumentParser) -> None:
    db_connection_args = parser.add_argument_group(
        "database connection arguments"
    )

    db_connection_args.add_argument(
        "-host",
        dest="host",
        type=str,
        required=True,
        help=("hostname of the database server"),
    )

    db_connection_args.add_argument(
        "-p",
        dest="port",
        type=int,
        required=True,
        help=("port of the database server"),
    )

    db_connection_args.add_argument(
        "-db",
        dest="database",
        type=str,
        required=True,
        help=("name of the database"),
    )

    db_connection_args.add_argument(
        "-u",
        dest="username",
        type=str,
        required=True,
        help=("user of the database"),
    )

    db_connection_args.add_argument(
        "-pwd",
        dest="password",
        type=str,
        required=True,
        help=("password of the database user"),
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gtd", description="Google trace data CLI tools"
    )

    subparsers = parser.add_subparsers(
        title="available subcommands", dest="cmd_name"
    )

    # Create parser for the "download" command
    download_parser = subparsers.add_parser(
        "download", help="download Google trace data (2019) from GCS"
    )
    add_download_args(download_parser)

    # Create parser for the "export" command
    export_parser = subparsers.add_parser(
        "export", help="export Google trace data (2019) to SQL database"
    )
    add_db_connection_args_group(export_parser)
    add_export_args(export_parser)

    # Create parser for the "ts" command
    ts_parser = subparsers.add_parser(
        "ts", help="handle timeseries of instances (tasks + alloc instances)"
    )
    add_ts_subparsers(ts_parser)

    return parser


def parse_command(
    args: List[str],
) -> Tuple[Union[str, None], argparse.Namespace]:
    parser = create_parser()

    pargs = parser.parse_args(args)

    if pargs.cmd_name is None:
        parser.print_usage()
        return None, pargs

    cmd_name = pargs.cmd_name
    del pargs.cmd_name

    return cmd_name, pargs
