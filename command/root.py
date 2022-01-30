import platform
import sys

from os import path
from .commons import *


def init(args):
    if not path.exists(NPG_REPO_PATH):
        setup_repo_cmd = as_privileged_cmd(['mkdir', '-p', f"{NPG_REPO_PATH}"])
        completed_or_exit(setup_repo_cmd)

    if path.exists(NPG_ROOT):
        print(f"Directory {NPG_ROOT} already exists", file = sys.stderr)
        sys.exit(1)

    system_release = platform.freedesktop_os_release()
    releasever = system_release['VERSION_ID']
    
    print(f"Creating build root {NPG_ROOT} for {system_release['ID']} {releasever} ...")
    install_cmd = as_privileged_cmd(['dnf', '-y', f"--releasever={releasever}", f"--installroot={NPG_ROOT}",
        'install', 'dnf', 'dnf-plugins-core', 'fedora-release', 'rpmdevtools', 'time', 'createrepo_c'])
    completed_or_exit(install_cmd)
    
    print(f"Setup build root ...")
    
    setup_result_cmd = as_bootstrap_cmd(['mkdir', NPG_WORKING_PATH, '/repo'])
    completed_or_exit(setup_result_cmd)

    setup_owner_cmd = as_bootstrap_cmd(['chmod', 'ugo+rwx', NPG_WORKING_PATH])
    completed_or_exit(setup_owner_cmd)

    setup_group_cmd = as_bootstrap_cmd(['groupadd', 'mock'])
    completed_or_exit(setup_group_cmd)
    
    setup_user_cmd = as_bootstrap_cmd(['useradd', '-M', f"--home={NPG_WORKING_PATH}", '--no-user-group', '--groups=mock', 'mockbuild'])
    # print(f"{setup_user_cmd}", file = sys.stderr)
    completed_or_exit(setup_user_cmd)   


def remove(args):
    if not path.exists(NPG_ROOT):
        sys.exit()

    print(f"Removing build root {NPG_ROOT} ...")
    command = as_privileged_cmd(['rm', '-rf', NPG_ROOT])
    completed_or_exit(command)


command_switcher = {
    'init': init,
    'remove': remove
}


def run(args):
    command_switcher.get(args.root_command)(args)