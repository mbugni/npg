import glob

from os import path
from .commons import *


def remove(args):
    if not path.exists(NPG_REPO_ROOT):
        sys.exit()

    print(f"Removing repo directory {NPG_REPO_ROOT} ...")
    command = as_privileged_cmd(['rm', '-rf'] + glob.glob(f"{NPG_REPO_ROOT}/*"))
    completed_or_exit(command)


command_switcher = {
    'remove': remove
}


def run(args):
    command_switcher.get(args.repo_command)(args)