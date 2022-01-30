import getpass
import shutil
import subprocess
import sys


NPG_BASE_PATH = '/var/npg'
NPG_ROOT = NPG_BASE_PATH + '/root'
NPG_REPO_PATH = '/repo'
NPG_REPO_ROOT = NPG_BASE_PATH + NPG_REPO_PATH
NPG_WORKING_PATH = '/result'
NPG_WORKING_ROOT = NPG_ROOT + NPG_WORKING_PATH
NPG_DOWNLOAD_PATH = NPG_WORKING_PATH + '/download'
NPG_RPMBUILD_PATH = NPG_WORKING_PATH + '/rpmbuild'
NPG_RPMBUILD_ROOT = NPG_ROOT + NPG_RPMBUILD_PATH
NPG_MACHINE_NAME='npg-machine'
NPG_REPO_NAME='npg-repo'


def run_as_privileged():
    if getpass.getuser() != 'root':
        completed = subprocess.run([shutil.which('sudo')] + sys.argv)
        sys.exit(completed.returncode)

def check_root_or_exit():
    if getpass.getuser() != 'root':
        print('You must be root to run this command', file=sys.stderr)
        sys.exit(1)

def as_privileged_cmd(command, env={}):
    check_root_or_exit()
    env_vars = []
    if env.keys():
        for env_key in env.keys():
            env_vars.append(env_key + '=' + env[env_key])
    return [shutil.which('env')] + env_vars + command

def as_bootstrap_cmd(command, env={}):
    nspawn_cmd = as_privileged_cmd(['systemd-nspawn', f"--directory={NPG_ROOT}", f"--machine={NPG_MACHINE_NAME}", '--quiet'], env=env)
    return nspawn_cmd + command

def as_machine_cmd(command):
    return as_bootstrap_cmd([f"--bind={NPG_REPO_ROOT}:{NPG_REPO_PATH}", '--bind=/tmp/npg:/tmp'] + command, env={'SYSTEMD_NSPAWN_TMPFS_TMP': '0'})

def completed_or_exit(command, capture_output=False, text=None):
    completed = subprocess.run(command, capture_output=capture_output, text=text)
    if completed.returncode:
         sys.exit(completed.returncode)
    return completed