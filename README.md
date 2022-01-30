# npg - Native Package Generator

## Purpose
A simple tool to build a RPM package from source in a systemd-nspawn container.

## How it works
NPG downloads source, builds using native options, and deploy the binary RPM in a local repo.

### Prepare the build root
```
$ npg root init
```
It prepares the build root for the current OS/version.

### Build a package from source
```
$ npg build hello
```
It downloads the SRPM and all required dependencies into the build root. Then the build process is started.
The result will be in `/var/npg/repo` folder.


### Replace a built package from local repo
```
$ npg replace hello
```
It replaces selected packages from `/var/npg/repo` folder. A transaction summary is printed before proceed.

### Getting more help
Use the `--help` option to get more info about the tool.


## Change Log
All notable changes to this project will be documented in the [`CHANGELOG.md`](CHANGELOG.md) file.

The format is based on [Keep a Changelog][01].

[01]: https://keepachangelog.com/
