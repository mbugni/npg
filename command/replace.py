import dnf
import dnf.base
import dnf.conf
import dnf.cli.cli
import dnf.cli.output

from .commons import *
from dnf.i18n import _


def install(args):
    if args.pkg_name:
        print(f"Trying to replace package {args.pkg_name} ...")
    else:
        print(f"Trying to replace all packages from local repo ...")

    # Base object for dnf operations: https://dnf.readthedocs.io/en/latest/api.html
    native_dnf = dnf.Base()
    native_dnf.conf.install_weak_deps = False
    native_dnf.output = dnf.cli.output.Output(native_dnf, native_dnf.conf)

    # Add local NPG repo to conf
    native_dnf.repos.add_new_repo(repoid=NPG_REPO_NAME, conf=native_dnf.conf, baseurl=['file://' + NPG_REPO_ROOT])

    # Retrieve metadata information about all known packages
    native_dnf.fill_sack()

    # Resolves package list from name (if any)
    native_query = native_dnf.sack.query()
    if args.pkg_name:
        native_query = native_query.filter(name__glob=args.pkg_name, reponame=NPG_REPO_NAME).latest()
    else:
        native_query = native_query.filter(reponame=NPG_REPO_NAME).latest()

    # print(f"Query {args.pkg_name} {native_query.run()}")
    for pkg in native_query.run():        
        # Check packages installed
        # print(f"{pkg} {pkg.installed}")
        resolve_query = native_dnf.sack.query().installed().filter(name=pkg.name, arch=pkg.arch)
        resolved = resolve_query.run()
        if resolved:
            # Package is installed, now check if it's upgradable
            upgrade_query = native_dnf.sack.query()
            upgrade_query = upgrade_query.upgrades().filter(name=pkg.name, reponame=NPG_REPO_NAME, arch=pkg.arch).latest()
            if upgrade_query.run():
                # print(f"Resolved upgrading {pkg.name}")
                native_dnf.package_upgrade(pkg)
            else:
                # print(f"Resolved reinstalling {pkg.name}")
                native_dnf.package_reinstall(pkg)
            
    native_dnf.resolve()
    # for item in native_dnf.transaction.install_set:
    #     print(f"install: {item}")
    # for item in native_dnf.transaction.remove_set:
    #     print(f"remove: {item}")
    
    if native_dnf.transaction.install_set:
        print(f"{native_dnf.output.list_transaction(native_dnf.transaction)}")
        if native_dnf.output.userconfirm():
            native_dnf.do_transaction(dnf.cli.output.CliTransactionDisplay())
    else:
        print(_('Nothing to do.'))

def run(args):
    install(args)
