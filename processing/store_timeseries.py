import argparse
import os

import pandas as pd

from sqlalchemy import create_engine

def get_args():
    parser = argparse.ArgumentParser(
        prog="sts",
        description="Store time series csv files in MySQL database"
    )

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

    return parser.parse_args()

def create_connection(host, port, username, password, database):
    db_string = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
    db = create_engine(db_string)
    return db.connect()

if __name__ == "__main__":
    args = get_args()

    path = args.input if args.input.endswith("/") else args.input + "/"
    con = create_connection(args.host, args.port, args.username, args.password, args.database)

    first_file = True
    for file in os.listdir(path):
        df = pd.read_csv(path + file)
        if first_file:
            policy = "replace"
            first_file = False
        else:
            policy = "append"
        df.to_sql(args.output, con, if_exists=policy, index=False)