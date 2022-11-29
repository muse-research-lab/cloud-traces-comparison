import argparse
import importlib
from collections import namedtuple
from typing import Dict

CommandInfo = namedtuple("CommandInfo", "module_path, class_name")

commands_dict: Dict[str, CommandInfo] = {
    "download": CommandInfo("gtd.cli.download", "DownloadCommand"),
    "export": CommandInfo("gtd.cli.export", "ExportCommand"),
}


class Command:
    def __init__(self, name: str) -> None:
        self.name = name

    def run(self, args: argparse.Namespace) -> int:
        raise NotImplementedError


def create_command(name: str) -> Command:
    """
    Create an instance of the Command class with the given name.
    """
    module_path, class_name = commands_dict[name]
    module = importlib.import_module(module_path)
    command_class = getattr(module, class_name)
    command: Command = command_class(name=name)

    return command
