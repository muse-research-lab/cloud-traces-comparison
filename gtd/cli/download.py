import argparse
import os
import subprocess
import sys
from typing import List

from gtd.cli.commands import Command


class DownloadCommand(Command):
    def run(self, args: argparse.Namespace) -> int:
        downloaded_files = self._download_data(
            args.cluster, args.table, args.pct, args.dst
        )

        self._unzip_data(args.dst, args.table, downloaded_files)

        return 0

    def _download_data(
        self, cluster: str, table: str, pct: int, dst: str
    ) -> List[str]:
        src_dir = f"gs://clusterdata_2019_{cluster}/"

        try:
            out = subprocess.run(
                ["gsutil", "list", src_dir], capture_output=True, check=True
            )
        except subprocess.CalledProcessError as exc:
            print(exc)
            sys.exit(-1)

        stdout = out.stdout
        raw_dir_items = stdout.splitlines()

        dir_items = []
        for raw_item in raw_dir_items:
            tmp_item = raw_item.decode().split("/")[-1]
            dir_items.append(tmp_item)

        total_items = [item for item in dir_items if item.startswith(table)]

        elems_to_keep = round(len(total_items) * pct / 100)
        items_to_download = total_items[:elems_to_keep]

        dst_dir = dst + table if dst.endswith("/") else dst + f"/{table}"
        dst_dir = os.path.abspath(dst_dir)

        dirExists = os.path.exists(dst_dir)
        if not dirExists:
            os.makedirs(dst_dir)

        for item in items_to_download:
            src = src_dir + item
            try:
                subprocess.run(["gsutil", "cp", src, dst_dir], check=True)
            except subprocess.CalledProcessError as exc:
                print(exc)
                sys.exit(-1)

        return items_to_download

    def _unzip_data(self, dst: str, table: str, items: List[str]) -> None:
        dst_dir = dst + table if dst.endswith("/") else dst + f"/{table}"
        dst_dir = os.path.abspath(dst_dir)

        for item in items:
            try:
                subprocess.run(["gunzip", item], check=True, cwd=dst_dir)
            except subprocess.CalledProcessError as exc:
                print(exc)
                sys.exit(-1)
