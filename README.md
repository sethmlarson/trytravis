# trytravis

[![Travis](https://img.shields.io/travis/SethMichaelLarson/trytravis/master.svg?style=flat)](https://travis-ci.org/SethMichaelLarson/trytravis)
[![AppVeyor](https://img.shields.io/appveyor/ci/SethMichaelLarson/trytravis/master.svg?style=flat)](https://ci.appveyor.com/project/SethMichaelLarson/trytravis)
[![Codecov](https://img.shields.io/codecov/c/github/SethMichaelLarson/trytravis/master.svg?style=flat)](https://codecov.io/gh/SethMichaelLarson/trytravis)
[![BountySource](https://img.shields.io/badge/donate-bountysource-brightgreen.svg?style=flat)](https://salt.bountysource.com/teams/trytravis)

Send your local git repository to Travis CI without needless commits and pushes.

## About

- Have you ever spent hours committing tiny changes, pushing, waiting for a specific job over and over again?
- Do your Pull Requests have 5 times as many commits as there are meaningful changes simply due to CI issues?
- Tired of complicated `git` commands in order to roll-back and delete useless commits from your history?

If any of these are true, `trytravis` is the tool for you.

## Installation and Usage

Here's a short guide on how to get started. If you've got questions or need
a clarification on any steps don't hesitate to open an issue. (Or one better,
open a Pull Request to fix the problem!)

### Supported Platforms

`trytravis` works on Linux, Windows, and Mac OS and only requires
Python 2.7 or Python 3.4 or later to be installed to run.

### Install the latest `trytravis` via [`pip`](https://pip.pypa.io/en/stable/):
```
bash-4.4$ pip install trytravis
bash-4.4$ trytravis --version
trytravis 1.0.0 (ubuntu 16.04.3 python 3.6.2)
```

### Optional: [Create a new GitHub account](https://help.github.com/articles/signing-up-for-a-new-github-account/).

You can create a new GitHub account to allow for higher utilization of Travis
builds so your `trytravis` builds don't conflict with regular builds.
Make sure to also register the account with Travis.

You can use your own GitHub account if you want as well.

### [Create a GitHub repository](https://github.com/new)

Here's a [guide on how to create a GitHub repository](https://help.github.com/articles/create-a-repo/).
Don't use an organization account as the owner of the repository.
Use the same account that you used to create this repository for the next step.

**IMPORTANT:** Make sure you don't use a repository where you have things you
don't want to be changed. This tool will make major changes to the repository.

**IMPORTANT** Make sure you can auto-commit to this repository
([such as by permanent authentication](https://stackoverflow.com/a/28562679))
to make things smoother.

### [Register the repository with Travis CI](https://docs.travis-ci.com/user/getting-started/)

Login to Travis, go to Accounts and turn the building on for the Repository. You
may need to use `Sync Account` if you don't see the repository in the available list.

### Tell `trytravis` which GitHub repository to use

Run `trytravis --repo` and enter in the URL to the repository that you just created.

### Ready to Use the Tool

Move to the base directory of your project and execute the following command:

  ```
  bash-4.4$ trytravis
  ```

After this if `trytravis` is able to detect your GitHub repository and local changes
you should see the following output from this command:

```
Adding a temporary remote to `https://github.com/SethMichaelLarson/throwaway`...
Adding all local changes...
Commiting local changes...
Pushing to `trytravis` remote...
Reverting to old state...
Waiting for a Travis build to appear for `d443d2e985812bd693e61e7093985a8e9451fad4f`...
Travis build id: `268589271`
Travis build URL: `https://travis-ci.org/SethMichaelLarson/throwaway/builds/268589271`

#1  P linux c python TOXENV=lint
#2  X linux c python TOXENV=lint
#3  X linux s python TOXENV=py27
#4  P linux c python TOXENV=py34
#5  P linux c python TOXENV=py35
#6  * linux s python TOXENV=py36
#7  *  osx  s python TOXENV=py27
#8  *  osx  c python TOXENV=py34
#9  *  osx  c python TOXENV=py35
#10 *  osx  s python TOXENV=py36
```

## Contributing

There are many ways to contribute to `trytravis`, even if you are not skilled in Python programming
including: Contributing financially via [BountySource](https://salt.bountysource.com/teams/trytravis),
opening pull requests, raising issues, updating documentation, spreading the word via social media,
and more! Check out [`CONTRIBUTING.md`](https://github.com/SethMichaelLarson/trytravis/blob/master/CONTRIBUTING.md)
for more information and guidelines to contributing.

## Future Improvements

- Support using SSH remotes (maybe via an option like `--ssh`?)
- Support for automatically cancelling builds on `Ctrl+C` after
  registering your Travis API token. (`--token`?)

## License

This project is licensed under `Apache-2.0`. Read [`LICENSE`](https://github.com/SethMichaelLarson/trytravis/blob/master/LICENSE) for more information.

```
 Copyright 2017 Seth Michael Larson

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
limitations under the License.
```

## Author

Follow me on Twitter [`@pythoasis`](https://twitter.com/pythoasis)
for updates on `trytravis` and other projects that I'm working on.
