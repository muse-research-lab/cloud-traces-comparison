import argparse
import os
from typing import List, Tuple, Union

import pandas as pd

from gtd.cli.commands import Command
from gtd.cli.utils import create_mysql_con
from gtd.visualization.plot_ts import (
    create_fig,
    get_split_col_intervals,
    reset_time,
    save_fig,
    sort_ts,
)


class TsCommand(Command):
    def run(self, args: argparse.Namespace) -> int:
        if args.ts_cmd_name == "create":
            return TsCreateCommand(name="ts create").run(args)
        elif args.ts_cmd_name == "export":
            return TsExportCommand(name="ts export").run(args)
        elif args.ts_cmd_name == "plot":
            return TsPlotCommand(name="ts plot").run(args)
        else:
            raise ValueError(
                f"{args.ts_cmd_name} is not a valid ts subcommand name!"
            )


class TsCreateCommand(Command):
    def run(self, args: argparse.Namespace) -> int:
        dst_dir = (
            args.output if args.output.endswith("/") else args.output + "/"
        )

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


class TsPlotCommand(Command):
    def run(self, args: argparse.Namespace) -> int:

        if os.path.isfile(args.input):
            files = [args.input]
        elif os.path.isdir(args.input):
            src_dir = (
                args.input if args.input.endswith("/") else args.input + "/"
            )
            files = [src_dir + file for file in os.listdir(args.input)]
        else:
            raise ValueError(f"'{args.input}' is not a valid file or dir name!")

        dst_dir = (
            args.output if args.output.endswith("/") else args.output + "/"
        )

        dirExists = os.path.exists(dst_dir)
        if not dirExists:
            os.makedirs(dst_dir)

        for file in files:
            df = pd.read_csv(file)
            sorted_df = sort_ts(df, "time")

            self._generate_figs(sorted_df, args, dst_dir)
        return 0

    def _generate_figs(
        self, df: pd.DataFrame, args: argparse.Namespace, dst_dir: str
    ) -> None:
        start_time = df["time"].iloc[0]
        end_time = df["time"].iloc[df.shape[0] - 1]
        x = reset_time(df["time"])

        intervals: List[Tuple[int, Union[None, int]]] = []
        if args.interval is None:
            intervals = [(0, None)]
        else:
            intervals = get_split_col_intervals(
                x, int(x.iloc[0]), x.iloc[x.shape[0] - 1], args.interval
            )

        uid = df["unique_id"].iloc[0]
        title = f"Instance: {uid}"
        xtitle = "Time (h)"
        ytitle = self._get_ytitle(args.metrics[0])
        labels = self._get_labels(args.metrics)

        for idx, elem in enumerate(intervals):
            llim, ulim = elem

            y_list = []
            for metric in args.metrics:
                y_list.append(df.iloc[llim:ulim][metric])

            fig = create_fig(
                x.iloc[llim:ulim],
                y_list,
                labels,
                title,
                xtitle,
                ytitle,
                0,
                args.lim,
            )
            path = f"{dst_dir}{uid}-{start_time}-{end_time}-{idx}.png"
            save_fig(fig, path)

    def _get_ytitle(self, metric: str) -> str:
        if "cpu" in metric:
            return "CPU usage"
        else:
            return "Memory usage"

    def _get_labels(self, metrics: List[str]) -> List[str]:
        labels = []
        for metric in metrics:
            if "limit" in metric:
                labels.append("limit")
            elif "random_sample" in metric:
                labels.append("random_sample")
            else:
                labels.append(metric.split("_")[0])

        return labels
