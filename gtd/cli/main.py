import sys
from typing import List, Optional

from gtd.cli.commands import create_command
from gtd.cli.parser import parse_command


def main(args: Optional[List[str]] = None) -> int:
    if args is None:
        args = sys.argv[1:]

    cmd_name, cmd_args = parse_command(args)

    if cmd_name is None:
        return 0
    else:
        command = create_command(cmd_name)
        return command.run(cmd_args)
