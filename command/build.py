import dnf
import dnf.conf
import glob
import os
import re

from .commons import *


def build(args):
    print(f"Preparing to build {args.pkg_name} ...")

    # System DNF to check package match
    system_dnf = dnf.Base()
    system_dnf.fill_sack()

    pkg_query = system_dnf.sack.query().filter(name__glob=args.pkg_name, latest_per_arch=True).latest()
    resolved = pkg_query.run()
    if len(resolved) != 1:
        print(f"Invalid package name: {args.pkg_name}")
        sys.exit(1)
    pkg = resolved[0]

    mkdir_tmp_cmd = as_privileged_cmd(['mkdir','-p','/tmp/npg'])
    completed_or_exit(mkdir_tmp_cmd)

    clean_cmd = as_privileged_cmd(['rm', '-rf'] + glob.glob(f"{NPG_WORKING_ROOT}/*") + glob.glob(f"{NPG_ROOT}/var/tmp/*") + glob.glob('/tmp/npg/*') )
    completed_or_exit(clean_cmd)

    setuptree_cmd = as_bootstrap_cmd(['env', f"HOME={NPG_WORKING_PATH}", 'rpmdev-setuptree'])
    completed_or_exit(setuptree_cmd)

    print(f"Getting {pkg.name} source and dependencies ...")

    download_cmd = as_bootstrap_cmd(['dnf','-y','download', f"--downloaddir={NPG_DOWNLOAD_PATH}",'--source', pkg.name])
    completed_or_exit(download_cmd)
    
    pkg_src_rpm = os.path.basename(glob.glob(f"{NPG_ROOT}{NPG_DOWNLOAD_PATH}/*.src.rpm")[0])
    builddep_cmd = as_bootstrap_cmd(['dnf','-y','builddep', f"{NPG_DOWNLOAD_PATH}/{pkg_src_rpm}"])
    completed_or_exit(builddep_cmd)

    print(f"Building {pkg.name} ...")
    rpm_optflags_cmd = as_bootstrap_cmd(['rpm', '--eval', '%{optflags}'])
    rpm_optflags_completed = completed_or_exit(rpm_optflags_cmd, capture_output=True, text=True)
    define_optflags = rpm_optflags_completed.stdout
    define_optflags = re.sub('\s+-m64\s+', ' -march=native ', define_optflags)
    define_optflags = re.sub('\s+-mtune=generic\s+',' -mtune=native ', define_optflags)

    rpmbuild_options = ['-rb','--nocheck','--nodeps']
    if not args.debuginfo:
        rpmbuild_options.append('--nodebuginfo')
    if args.cpus > 0:
        rpmbuild_options.extend(['--define', f"_smp_build_ncpus {args.cpus}"])
        rpmbuild_options.extend(['--define', f"_smp_mflags -j{args.cpus}"])
    rpmbuild_cmd = as_machine_cmd(['time','-p','rpmbuild'] + rpmbuild_options + [
        '--define', f"_topdir {NPG_RPMBUILD_PATH}", '--define', f"optflags {define_optflags}",
        '--define', f"packager Native Package Generator", f"{NPG_DOWNLOAD_PATH}/{pkg_src_rpm}"])
    completed_or_exit(rpmbuild_cmd)

    print(f"Populating repo ...")

    rpm_files = glob.glob(f"{NPG_RPMBUILD_ROOT}/RPMS/**/*.rpm", recursive=True)
    for rpm_file in rpm_files:
        rpm_file_name = os.path.basename(rpm_file)
        rpm_move_cmd = as_privileged_cmd(['mv', '--force', rpm_file, f"{NPG_REPO_ROOT}/{rpm_file_name}"])
        completed_or_exit(rpm_move_cmd)
    createrepo_cmd = as_machine_cmd(['createrepo_c', '--update', NPG_REPO_PATH])
    completed_or_exit(createrepo_cmd)


def run(args):
    build(args)
