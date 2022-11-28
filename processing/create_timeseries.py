import argparse

import pandas as pd

from sqlalchemy import create_engine

def get_args():
    parser = argparse.ArgumentParser(
        prog="cts",
        description="Create time series csv files"
    )

    parser.add_argument(
        "input",
        metavar="input",
        type=str,
        help="input file that contains tuples (collection_id, instance_index, upper_limit, lower_limit)",
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
        "-t",
        dest="table",
        type=str,
        required=True,
        help=(
            "name of the database table to read from"
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

def get_task_df(con, table, collection_id, instance_index):
    q = f"SELECT * FROM {table} WHERE collection_id = {collection_id} AND instance_index = {instance_index};"
    return pd.read_sql(q, con)

def sort_task_df(df, column, asc=True):
    return df.sort_values(column, ascending=asc)

if __name__ == "__main__":
    args = get_args()

    con = create_connection(args.host, args.port, args.username, args.password, args.database)

    with open(args.input, 'r') as f:
        lines = [line.rstrip() for line in f]
        tasks = [line.split() for line in lines]

    for cid, idx, llim, ulim in tasks:
        df = get_task_df(con, args.table, cid, idx)
        sorted_df = sort_task_df(df, "time", True)

        llim = int(llim)
        ulim = int(ulim)
        start_time = sorted_df.iloc[llim]["time"]
        end_time = sorted_df.iloc[ulim-1]["time"]
        file_name = f"{cid}-{idx}-{start_time}-{end_time}.csv"
        
        sorted_df[llim:ulim].to_csv(file_name, index=False)
