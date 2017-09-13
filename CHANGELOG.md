<!---
Add all non-trivial changes to this list along with your
name, the change type, the pull request number, issue number,
and issue reporter if applicable. Make sure to add hyperlinks for
issue and pull request numbers.
-->

# Changelog

All notable changes to trytravis will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Output Travis URL and stop. #17 Reported by @miguelbalparda

## 1.0.4

### Fixed

- Issue where `committed_at` would not be normalized to UTC. #18 Reported by @einball

## 1.0.3

### Changed

- Can no longer use a repository without containing the name `trytravis`.
  This is to prevent accidentally using a repository the user didn't intend
  to call with `git push -f`.

## 1.0.2

### Fixed

- Issue where if `env` isn't defined in `.travis.yml` then the
  script will error out with `KeyError`. #12 Reported by @eeeebbbbrrrr.

## 1.0.1

### Added

- Better message when running from a non-git repository.

### Fixed

- When running multiple times with the same commit hash `trytravis` would sometimes
  find and watch the incorrect build.
- `trytravis` would display an HTTPS URL even if an SSH URL was used in the output.

## 1.0.0

### Added

- Added the ability to read your repository slug from the local config.
- Added ability to add repository directly via command line with --repo option.
- Added the main functionality to trigger and watch Travis builds.
- Added ability to use `ssh://git@github.com/[USERNAME]/[REPOSITORY]` formatted remote urls.

### Changed

- Flattened the structure of all functions. Adhered to PEP8.
