# Changelog

## [Unreleased]

- log management
- start time and timezone configuration

## [1.2.0] - 2019-09-11

### Added

- NEW FEATURE: weighted task: user can now assign a percentage to a task id. Unweighted task randomly complete the period if needed.
- relatives check and warnings
- NEW FEATURE: recap before login: allow to avoid mistake
- virtualenv
- dev environment availability

### Changed

- outputs are more clear

### Fixed

- large period warning was not working due to error in business day count (missusage of library)
