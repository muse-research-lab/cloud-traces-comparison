import argparse

import os
import sys
import subprocess

def get_args():
    parser = argparse.ArgumentParser(
        prog="gtd",
        description="Download Google trace data (2019) from GCS"
    )

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
        choices=["collection_events", "instance_events", "instance_usage", "machine_attributes", "machine_events"],
        help="table of the requested trace [collection_events, instance_events, instance_usage, machine_attributes, machine_events]",
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
        dest="pct"
    )

    return parser.parse_args()

def validate_dst_path(path):
    if not os.path.isdir(path):
        print(f"Error: The specified path '{path}' does not exist.", file=sys.stderr)
        sys.exit()

def download_data(cluster, table, pct, dst):
    src_dir = f"gs://clusterdata_2019_{cluster}/"
    
    try:
        out = subprocess.run(["gsutil", "list", src_dir], capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        print(exc)
        sys.exit()

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
            sys.exit()
    
    return items_to_download

def unzip_data(dst, table, items):
    dst_dir = dst + table if dst.endswith("/") else dst + f"/{table}"
    dst_dir = os.path.abspath(dst_dir)

    for item in items:
        try:
            subprocess.run(["gunzip", item], check=True, cwd=dst_dir)
        except subprocess.CalledProcessError as exc:
            print(exc)
            sys.exit()

if __name__ == "__main__":
    args = get_args()

    validate_dst_path(args.dst)
    
    downloaded_files = download_data(args.cluster, args.table, args.pct, args.dst)

    unzip_data(args.dst, args.table, downloaded_files)