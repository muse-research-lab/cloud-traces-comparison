import argparse
import os

import pandas as pd

from gtd.cli.commands import Command
from gtd.cli.utils import create_mysql_con


class TsCommand(Command):
    def run(self, args: argparse.Namespace) -> int:
        if args.ts_cmd_name == "create":
            return TsCreateCommand(name="ts create").run(args)
        elif args.ts_cmd_name == "export":
            return TsExportCommand(name="ts export").run(args)
        else:
            raise ValueError(
                f"{args.ts_cmd_name} is not a valid ts subcommand name!"
            )


class TsCreateCommand(Command):
    def run(self, args: argparse.Namespace) -> int:
        dst_dir = args.output if args.output.endswith("/") else args.output + "/"
        
        con = create_mysql_con(
            args.host, args.port, args.username, args.password, args.database
        )

        dirExists = os.path.exists(dst_dir)
        if not dirExists:
            os.makedirs(dst_dir)
        
        with open(args.input, "r") as f:
            lines = [line.rstrip() for line in f]
            instances = [line.split() for line in lines]

        for cid, idx, llim, ulim in instances:
            q = f"""
                SELECT * FROM {args.table}
                WHERE collection_id = {cid} AND instance_index = {idx};
                """
            df = pd.read_sql(q, con)
            sorted_df = df.sort_values("time", ascending=True)

            llim_ = int(llim)
            ulim_ = int(ulim)
            start_time = sorted_df.iloc[llim_]["time"]
            end_time = sorted_df.iloc[ulim_ - 1]["time"]
            file_name = f"{cid}-{idx}-{start_time}-{end_time}.csv"

            sorted_df[llim_:ulim_].to_csv(dst_dir + file_name, index=False)

        return 0


class TsExportCommand(Command):
    def run(self, args: argparse.Namespace) -> int:
        path = args.input if args.input.endswith("/") else args.input + "/"
        con = create_mysql_con(
            args.host, args.port, args.username, args.password, args.database
        )

        first_file = True
        for file in os.listdir(path):
            df = pd.read_csv(path + file)
            if first_file:
                policy = "replace"
                first_file = False
            else:
                policy = "append"
            df.to_sql(args.output, con, if_exists=policy, index=False)

        return 0
