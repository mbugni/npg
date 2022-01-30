#!/usr/bin/python3
import argparse

from command.commons import run_as_privileged

argparser = argparse.ArgumentParser(description='Native Package Generator.')
argparser.add_argument('--verbose', help='print additional info to stderr', action='store_true')

arg_subparsers = argparser.add_subparsers(title='commands', dest='command')

build_parser = arg_subparsers.add_parser('build')
build_parser.add_argument('pkg_name', metavar='PACKAGE_NAME', help='The package name to build')
build_parser.add_argument('--cpus', type=int, default=0, metavar='NR_OF_CPUS', help='Max number of cores to use')
build_parser.add_argument('--debuginfo', default=False, action='store_true', help='Also generate debuginfo packages')
build_parser.add_argument('--upgrade', default=False, action='store_true', help='Use new version if available')

install_parser = arg_subparsers.add_parser('replace')
install_parser.add_argument('pkg_name', metavar='PACKAGE_NAME', nargs='?', default=None, help='The package name to replace')

repo_parser = arg_subparsers.add_parser('repo')
repo_subparsers = repo_parser.add_subparsers(title='repo commands', dest='repo_command')
repo_clean = repo_subparsers.add_parser(name='remove', help='Remove the package repo, warning: all built packages will be lost!')

root_parser = arg_subparsers.add_parser('root')
root_subparsers = root_parser.add_subparsers(title='root commands', dest='root_command')
root_init = root_subparsers.add_parser(name='init', help='Initialize the build root')
root_clean = root_subparsers.add_parser(name='remove', help='Remove the build root (do not remove local repo)')
root_configure = root_subparsers.add_parser(name='configure', help='Configure/reconfigure the build root')


def build(args):
    import command.build
    command.build.run(args)

def replace(args):
    import command.replace
    command.replace.run(args)

def root(args):
    import command.root
    command.root.run(args)

def repo(args):
    import command.repo
    command.repo.run(args)

command_switcher = {
    'build': build,
    'replace': replace,
    'repo': repo,
    'root': root
}

def main():
    args = argparser.parse_args()
    if args.command:
        run_as_privileged()
        command_switcher.get(args.command)(args)

if __name__ == "__main__":
    main()
    