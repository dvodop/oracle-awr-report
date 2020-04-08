# Changelog
All notable changes to this project will be documented in this file.

## [unreleased]
### Added
- atop_parser.sh lvm support
- atop_parser.sh per user cpu/memory statistic support
### Changed
- logging
### Fixed
- RedoStat query
- atop dsk columns config

## [1.1.0] - 2019.04.24
### Added
- plugin support
- SSH plugin
- shell script atop_parser.sh for gather atop data
- scatter charts support for custom charts
### Removed
- command line arguments support

## [1.0.1] - 2018.10.09
### Added
- date to workbook file name
- dbname to custom charts titles
- configuration parameters HOST,PORT,SID,SERVICE_NAME as an alternative to TNS_ALIAS
- reading password from command line, when it not preset in config file
- command line arguments support
### Fixed
- bug in DEBUG logging
- opening config files with utf-8 encoding

## [1.0.0] - 2018-09-24
###
- Initial release of oracle awr report python script
